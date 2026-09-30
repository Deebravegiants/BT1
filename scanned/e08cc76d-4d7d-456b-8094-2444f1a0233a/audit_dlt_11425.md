# [?] fix: add custom styles and overflow to avoid collapse of UI when selecting tabs on smaller screens

## Summary
Severity: Unknown
Chain: ZK
Component: semaphore-protocol/semaphore
Published: 2023-12-12
Source: https://github.com/semaphore-protocol/semaphore/commit/4600fa0b4844d753a77fb800827d8c91185592c3
Type: security-commit

## Details
fix: add custom styles and overflow to avoid collapse of UI when selecting tabs on smaller screens

Former-commit-id: 975ff06a0b7fa734d405abe6bc87c1cd4960bce9

## Patch
### apps/website/src/app/learn/page.tsx
```diff
@@ -290,17 +290,16 @@ await verifyProof(verificationKey, fullProof)`,
                     mt={{ base: "100px", md: "170px" }}
                     mb={{ base: "50px", md: "112px" }}
                 >
-                    <Box overflow="auto" mx="3">
-                        <TabList gap="40px" w="max-content" whiteSpace="nowrap">
-                            <Tab px={0} fontSize="24px">
+                    <Box mx="3" overflowX={{ base: "auto", md: "hidden" }}>
+                        <TabList gap="40px" w={{ base: "150%", md: "max-content" }} whiteSpace="nowrap" pl="4">
+                            <Tab px={0} fontSize="24px" _selected={{ borderBottom: "2px solid white" }}>
                                 About Semaphore
                             </Tab>
-                            <Tab px={0} fontSize="24px">
+                            <Tab px={0} fontSize="24px" _selected={{ borderBottom: "2px solid white" }}>
                                 About Zero Knowledge
                             </Tab>
                         </TabList>
                     </Box>
-                    <TabIndicator mt="-1.5px" height="2px" bg="white" borderRadius="1px" />
                     <TabPanels mt="80px">
                         <TabPanel>{renderTabBlockSemaphore()}</TabPanel>
                         <TabPanel>{renderTabBlockZeroKnowledge()}</TabPanel>
```
