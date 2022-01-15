# This is a minimal template for Pyside/PyQt QAbstractItemModel with typehints
# based on documentation from https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractItemModel.html

import dataclasses
import typing
from imflib import imf, cpl, pkl
from PySide6 import QtCore, QtGui
from dataclasses import dataclass

class CPLItem():

	def __init__(self, item_data:typing.Any):

		self._parent = None
		self._children = list()
		self._item_data =  item_data

	def getChild(self, row:int) -> typing.List["CPLItem"]:
		"""Return a child from a specified row"""
		return self._children[row] if row < self.child_count else None
	
	def addChild(self, child:"CPLItem"):
		"""Add a new child item"""
		child._parent = self
		self._children.append(child)
	
	def getChildIndex(self, child:"CPLItem") -> int:
		"""Get the index of a given child"""
		return self._children.index(child)
	
	def getData(self, column:int) -> typing.Any:
		"""Return the data for a given column"""
		return self._item_data
	
	@property
	def child_count(self) -> int:
		"""Number of children"""
		return len(self._children)
	
	@property
	def parent(self) -> "CPLItem":
		"""Return the parent item"""
		return self._parent
	
	@property
	def row(self) -> int:
		"""Figure out our index in our parent's child list"""
		return self._parent.getChildIndex(self) if self._parent else 0
	
	@property
	def column_count(self) -> int:
		"""Number of data items"""
		return len(self._item_data)

class SegmentItem(CPLItem):
	"""A Segment Node Item"""

class SequenceItem(CPLItem):
	"""A Sequence node item"""

class ResourceItem(CPLItem):
	"""A Resource node item"""



class CPLModel(QtCore.QAbstractItemModel):


	def __init__(self, imf:imf.Imf):

		super().__init__()

		self.headers = [
			"In Point",
			"Out Point",
			"File ID"
		]

		self._root = CPLItem(None)
		self._parseImf(imf)

	def _parseImf(self, imf:imf.Imf):
		"""Build the data model from the given IMF"""

		# First the Segments
		for seg in imf.cpl.segments:
			seg_item = SegmentItem(seg)
			self._root.addChild(seg_item)
			
			# Then sequences
			for seq in seg.sequences:
				seq_item = SequenceItem(seq)
				seg_item.addChild(seq_item)
				
				# And finally resources
				for res in seq.resources:
					res_item = ResourceItem(res)
					seq_item.addChild(res_item)
					

	def index(self, row:int, column:int, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""

		# TODO: Investigate
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()

		if not parent.isValid():
			# TODO: This is probably not right but is working for now
			cpl_item = self._root.getChild(row)
			# Probably this
			#cpl_item = self._root
		else:
			cpl_item = parent.internalPointer().getChild(row)
		
		if cpl_item:
			return self.createIndex(row, column, cpl_item)
		else:
			return QtCore.QModelIndex()
	
	def parent(self, child_index:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""

		# Probably won't happen
		if not child_index.isValid():
			return QtCore.QModelIndex()
		
		parent_item = child_index.internalPointer().parent

		# TODO: Think about it
		if parent_item is None:
			print(f"Returning invalid for {parent_item}")
			return QtCore.QModelIndex()
		
		else:
			return self.createIndex(parent_item.row, 0, parent_item)


		
	def rowCount(self, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""

		# Only column 0 should have child rows here
		if parent.column() > 0:
			return 0
		
		if not parent.isValid():
			return self._root.child_count
		else:
			return parent.internalPointer().child_count
	
	def columnCount(self, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""
		return len(self.headers)

	def data(self, index:QtCore.QModelIndex, role:typing.Optional[int]=QtCore.Qt.DisplayRole) -> typing.Any:
		"""Returns the data stored under the given role for the item referred to by the index."""

		if not index.isValid():
			return "Woahahey"

		item = index.internalPointer()
		
		if role == QtCore.Qt.DisplayRole:
			return str(type(item.getData(0)))
		

	def headerData(self, column:int, orientation:QtCore.Qt.Orientation, role:typing.Optional[int]=QtCore.Qt.DisplayRole) -> typing.Any:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		
		if role == QtCore.Qt.DisplayRole:
			return self.headers[column]
		