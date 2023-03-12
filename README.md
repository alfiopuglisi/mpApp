A framework for multiprocessing Python apps exchanging data via shared memory, including numpy arrays. Useful if your app is:
   * Composed of multiple processes processing data at high speed, with or without dependencies between them
   * Communication between processes is done via push/pull of numpy arrays
   * Can be optionally distributed over the network (it will go slower of course)
   
Shared memory records are built on top of ctypes.Structure.
