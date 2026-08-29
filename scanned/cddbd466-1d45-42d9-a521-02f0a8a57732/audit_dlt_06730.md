# [M] addbridgeagentfactory in rootPort is not functional

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-maia
Published: 2023-06-29
Source: https://github.com/code-423n4/2023-05-maia-findings/issues/372
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-maia/blob/78e49c651fd119b85bb79296620d5cb39efa7cdd/src/ulysses-omnichain/RootPort.sol#L406-L410


# Vulnerability details

## Impact
the addbridgeagentfactory function is responsible for adding a new bridge agent factory to the root port. 

However the current implementation is faulty. the faulty logic is in the following line: 
    
    bridgeAgentFactories[bridgeAgentsLenght++] = _bridgeAgentFactory;

a couple of problems here, the function is attempting to access an index that does not yet exist in the bridgeAgentFactories array, this should return an out of bounds error. the function also does not update the isBridgeAgentFactory mapping. once a a new bridge agent factory is added, a new dict item with key equal to address of new bridge agent factory and value of true. this mapping is then used to enable toggling the factory, ie enabling or disabling it via the toggleBridgeAgentFactory function.

Impact: the code hints that this is a key governance action. it does not work at the moment however with regards to impact, at this moment it is unclear from the code what the overall impact would be to the functioning of the protocol, that is why it is rated as medium rather than high. feedback from sponsors is welcome to determine severity.

## Proof of Concept
        function testAddRootBridgeAgentFactoryBricked() public {
        //Get some gas
        hevm.deal(address(this), 1 ether);

        RootBridgeAgentFactory newBridgeAgentFactory = new RootBridgeAgentFactory(
            ftmChainId,
            WETH9(ftmWrappedNativeToken),
            localAnyCallAddress,
            address(ftmPort),
            dao
        );

        rootPort.addBridgeAgentFactory(address(newBridgeAgentFactory));
        
        require(rootPort.bridgeAgentFactories(0)==address(bridgeAgentFactory), "Initial Factory not in factory list");
        require(rootPort.bridgeAgentFactories(1)==address(newBridgeAgentFactory), "New Factory not in factory list");
    
    }


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-maia-findings/issues/372_
