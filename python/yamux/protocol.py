# -*- coding: utf-8 -*-

import enum
import six
import struct


class Version(enum.IntEnum):
    """
    The version field is used for future backward compatibility. At the
    current time, the field is always set to 0, to indicate the initial
    version.
    """
    Initial = 0

class FrameType(enum.IntEnum):
    """
    The type field is used to switch the frame message type. The following
    message types are supported:

    * 0x0 Data - Used to transmit data. May transmit zero length payloads
      depending on the flags.

    * 0x1 Window Update - Used to updated the senders receive window size.
      This is used to implement per-session flow control.

    * 0x2 Ping - Used to measure RTT. It can also be used to heart-beat
      and do keep-alives over TCP.

    * 0x3 Go Away - Used to close a session.
    """

    # Data is used for data frames. They are followed
    # by length bytes worth of payload.
    Data = 0

    # WindowUpdate is used to change the window of
    # a given stream. The length indicates the delta
    # update to the window.
    WindowUpdate = 1

    # Ping is sent as a keep-alive or to measure
    # the RTT. The StreamID and Length value are echoed
    # back in the response.
    Ping = 2

    # GoAway is sent to terminate a session. The StreamID
    # should be 0 and the length is an error code.
    GoAway = 3

class Flags(enum.IntEnum):
    """
    The flags field is used to provide additional information related
    to the message type. The following flags are supported:

    * 0x1 SYN - Signals the start of a new stream. May be sent with a data or
      window update message. Also sent with a ping to indicate outbound.

    * 0x2 ACK - Acknowledges the start of a new stream. May be sent with a data
      or window update message. Also sent with a ping to indicate response.

    * 0x4 FIN - Performs a half-close of a stream. May be sent with a data
      message or window update.

    * 0x8 RST - Reset a stream immediately. May be sent with a data or
      window update message.
    """

    # SYN is sent to signal a new stream. May
    # be sent with a data payload
    SYN = 1

    # ACK is sent to acknowledge a new stream. May
    # be sent with a data payload
    ACK = 2

    # FIN is sent to half-close the given stream.
    # May be sent with a data payload.
    FIN = 4

    # RST is used to hard close a given stream.
    RST = 8

# When Yamux is initially starts each stream with a 256KB window size.
# There is no window size for the session.

# To prevent the streams from stalling, window update frames should be
# sent regularly. Yamux can be configured to provide a larger limit for
# windows sizes. Both sides assume the initial 256KB window, but can
# immediately send a window update as part of the SYN/ACK indicating a
# larger window.

# Both sides should track the number of bytes sent in Data frames
# only, as only they are tracked as part of the window size.
InitialStreamWindow = 256 * 1024

class Error(enum.IntEnum):
    """
    When a session is being terminated, the Go Away message should
    be sent. The Length should be set to one of the following to
    provide an error code
    """

    # Normal is sent on a normal termination
    Normal = 0

    # ProtoErr sent on a protocol error
    ProtoErr = 1

    # InternalErr sent on an internal error
    InternalErr = 2

class Frame(six.binary_type):
    """
    Yamux uses a streaming connection underneath, but imposes a message
    framing so that it can be shared between many logical streams. Each
    frame contains a header like:

    * Version (8 bits)
    * Type (8 bits)
    * Flags (16 bits)
    * StreamID (32 bits)
    * Length (32 bits)

    This means that each header has a 12 byte overhead.
    All fields are encoded in network order (big endian).
    """
    HeaderLength = 12

    @staticmethod
    def Create(version=Version.Initial, frameType=FrameType.Data, flags=0, streamID=0, data=b''):
        return Frame(struct.pack('!BBHII', version, frameType, flags, streamID, len(data)) + data)

    def __repr__(self):
        return '<%s(version=%r, frameType=%r, flags=%r, streamID=%r, length=%r)>' % (self.__class__.__name__, self.version, self.frameType, self.flags, self.streamID, self.length)

    @property
    def version(self):
        return Version(struct.unpack('!B', self[0:1])[0])

    @property
    def frameType(self):
        return FrameType(struct.unpack('!B', self[1:2])[0])

    @property
    def flags(self):
        return struct.unpack('!H', self[2:4])[0]

    @property
    def streamID(self):
        return struct.unpack('!I', self[4:8])[0]

    @property
    def length(self):
        return struct.unpack('!I', self[8:12])[0]    
    
    @property
    def body(self):
        return self[12:12+self.length]

    @property
    def next(self):
        return self[12+self.length:]
