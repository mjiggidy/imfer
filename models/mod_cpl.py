# This is a minimal template for Pyside/PyQt QAbstractItemModel with typehints
# based on documentation from https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractItemModel.html

import typing
from imflib import imf, cpl, pkl
from PySide6 import QtCore

class CPLModel(QtCore.QAbstractItemModel):
	"""Qt Data Model Adapter for CPL"""

	def __init__(self, imf:imf.Imf):
		"""Create and setup a new model"""
		super().__init__()

		self._headers = [
			"Name",
			"Record In",
			"Record Out",
			"Source In",
			"Source Out",
			"Rate"
		]

		self.imf = imf
		
		# Typically a list of data here
		# Typically a dict of header keys and values here
	
	def index(self, row:int, column:int, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""

		
		if not parent.isValid():
			# Top-level... gonna assume we talkin segments here
			print("Returning ",(self.imf.cpl.segments[row], parent))
			return self.createIndex(row, column, (self.imf.cpl.segments[row], parent))
		
		item, par = parent.data()
		
		if isinstance(item, cpl.Segment):
			print("Returning ",(item.sequences[row], parent))
			return self.createIndex(row, column, (item.sequences[row], parent))
		
		elif isinstance(item, cpl.Sequence):
			print("Returning",(item.resources[row], parent))
			return self.createIndex(row, column, (item.resources[row], parent))
		
		else:
			print("Rreturning HHHNNNNOOOTHING")
			return QtCore.QModelIndex()
				
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""

		item, parent = child.data()
		return parent

	def rowCount(self, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""


		if not parent.isValid():
			# Top-level... gonna assume we talkin segments here
			return len(self.imf.cpl.segments)
		
		item, par = parent.data()

		if isinstance(item, cpl.Segment):
			return len(item.sequences)			
		
		elif isinstance(item, cpl.Sequence):
			return len(item.resources)
		
		else:
			return 0
	
	def columnCount(self, parent:typing.Optional[QtCore.QModelIndex]=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""

		if parent.isValid() and isinstance(parent.data()[0], cpl.Sequence):
			return len(self._headers)
		
		else:
			return 1

	def data(self, index:QtCore.QModelIndex, role:typing.Optional[int]=QtCore.Qt.DisplayRole) -> typing.Any:
		"""Returns the data stored under the given role for the item referred to by the index."""

		item, par = index.data()

		if role == QtCore.Qt.DisplayRole:

			if isinstance(item, cpl.Resource):
				if index.column() == 0:
					return item.file_id
				elif index.column() == 1:
					return str(item.in_point)	# I know...
				elif index.column() == 2:
					return str(item.out_point)	# ...I know.
				elif index.column() == 3:
					return str(item.in_point)
				elif index.column() == 4:
					return str(item.out_point)
				elif index.column() == 5:
					return str(item.edit_rate_formatted)
				else:
					return "Unknown!"



	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:typing.Optional[int]=QtCore.Qt.DisplayRole) -> typing.Any:
		"""Returns the data for the given role and section in the header with the specified orientation."""

		if role == QtCore.Qt.DisplayRole:
			return self._headers[section]