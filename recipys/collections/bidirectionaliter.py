"""
Example.

.. code::python

  rick_and_morty_forever = BiDirectionalIter(['rick', 'morty'])
  while True:
    print rick_and_morty_forever.next()

.. code::bash

  rick
  morty
  rick
  morty
  rick
  morty

Rick and Morty forever and forever 100 years! Using the .set_direction_reverse method will cause the output to
"morty" and then "rick".
"""

from collections import Iterator

class BiDirectionalIter(Iterator):
    """
    An iterator the can be iterated over indefinitely in both directions.

    :param list elements: List of elements to iterate over.
    :param int starting_index: Index to start iteration from.
    """

    def __init__(self, elements, starting_index=0):
        self._elements = elements
        self._index = starting_index
        self._direction = 1
        self._length = len(self._elements)

    def next(self):
        """
        Return the next element in :class:`BiDirectionalIter` based
        on the current direction.
        """
        self._index = (self._index + self._direction) % self._length
        return self._elements[self._index]

    def set_direction_forward(self):
        """
        Set the direction of iteration from left to right.
        """
        self._direction = 1

    def set_direction_reverse(self):
        """
        Set the direction of iteration from right to left.
        """
        self._direction = -1
