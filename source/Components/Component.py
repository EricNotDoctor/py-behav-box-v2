from abc import ABCMeta, abstractmethod
from enum import Enum


class Component:
    __metaclass__ = ABCMeta
    """
        Abstract class defining the base requirements for a feature that receives input from or outputs to a Source

        Parameters
        ----------
        source : Source
            The Source related to this Component
        component_id : str
            The ID of this Component
        component_address : str
            The location of this Component for its Source
        metadata : str
            String containing any metadata associated with this Component
        
        Attributes
        ----------
        id : str
            The ID of this Component
        address : str
            The location of this Component for its Source
        source : Source
            The Source related to this Component
        
        Methods
        -------
        get_state()
            Returns the current state the component is in (no type restrictions)
        get_type()
            Returns the Type of this Component
    """

    class Type(Enum):
        DIGITAL_INPUT = 0  # The Component solely provides digital input
        DIGITAL_OUTPUT = 1  # The Component solely receives digital output
        ANALOG_INPUT = 2  # The Component solely provides analog input
        ANALOG_OUTPUT = 3  # The Component solely receives analog output
        INPUT = 4  # Arbitrary input type
        OUTPUT = 5  # Arbitrary output type
        BOTH = 6  # The Component both inputs and outputs (arbitrary type)

    def __init__(self, source, component_id, component_address):
        self.id = component_id  # The unique identifier for the component or set of related components
        self.address = component_address  # The platform-specific address for the component
        self.source = source  # The source that is used to identify the component

    def write(self, msg):
        self.source.write_component(self.id, msg)

    def read(self):
        return self.source.read_component(self.id)

    def initialize(self, metadata):
        for key in metadata:
            if hasattr(self, key):
                setattr(self, key, metadata[key])

    @abstractmethod
    def get_state(self): raise NotImplementedError

    @abstractmethod
    def get_type(self): raise NotImplementedError

    def close(self):
        self.source.close_component(self.id)

