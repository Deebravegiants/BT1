# [?] Merge #18515: test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-04-05
Source: https://github.com/litecoin-project/litecoin/commit/cf21293ef7fd304efb0843abeb17adc6159ca927
Type: security-commit

## Details
Merge #18515: test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

0ed2d8e07d3806d78d03a77d2153f22f9d733a07 test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py (Sebastian Falbesoner)

Pull request description:

  Integrates the missing message type `filteradd` to the test framework and checks that the BIP37 implementation is not vulnerable to the "remote crash bug" [CVE-2013-5700](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2013-5700) anymore. Prior to v.0.8.4, it was possible to trigger a division-by-zero error on the following line in the function `CBloomFilter::Hash()`:
  https://github.com/bitcoin/bitcoin/blob/f0d6487e290761a4fb03798240a351b5fddfdb38/src/bloom.cpp#L45
  By setting a zero-length filter via `filterload`, `vData.size()` is 0, so the modulo operation above, called on any .insert() or .contains() operation then crashed the node. The test uses the approach of just sending an arbitrary `filteradd` message after, which calls `CBloomFilter::insert()` (and in turn `CBloomFilter::Hash()`) on the node. The vulnerability was fixed by commit https://github.com/bitcoin/bitcoin/commit/37c6389c5a0ca63ae3573440ecdfe95d28ad8f07 (an intentional covert fix, [according to gmaxwell](https://github.com/bitcoin/bitcoin/issues/18483#issuecomment-608224095)), which introduced flags `isEmpty`/`isFull` that wouldn't call the `Hash()` member function if `isFull` is true (set to true by default constructor).

  To validate that the test fails if the implementation is vulnerable, one can simply set the flags to false in the member function `UpdateEmptyFull()` (that is called after a filter received via `filterload` is constructed), which activates the vulnerable code path calling `Hash` in any case on adding or testing for data in the filter:
  ```diff
  diff --git a/src/bloom.cpp b/src/bloom.cpp
  index bd6069b..ef294a3 100644
  --- a/src/bloom.cpp
  +++ b/src/bloom.cpp
  @@ -199,8 +199,8 @@ void CBloomFilter::UpdateEmptyFull()
           full &= vData[i] == 0xff;
           empty &= vData[i] == 0;
       }
  -    isFull = full;
  -    isEmpty = empty;
  +    isFull = false;
  +    isEmpty = false;
   }
  ```
  Resulting in:
  ```
  $ ./p2p_filter.py
  [...]
  2020-04-03T14:38:59.593000Z TestFramework (INFO): Check that division-by-zero remote crash bug [CVE-2013-5700] is fixed
  2020-04-03T14:38:59.695000Z TestFramework (ERROR): Assertion failed
  [...]
  [... some exceptions following ...]
  ```

ACKs for top commit:
  naumenkogs:
    utACK 0ed2d8e07d3806d78d03a77d2153f22f9d733a07

Tree-SHA512: 02d0253d13eab70c4bd007b0750c56a5a92d05d419d53033523eeb3ed80318bc95196ab90f7745ea3ac9ebae7caee3adbf2a055a40a4124e0915226e49018fe8
