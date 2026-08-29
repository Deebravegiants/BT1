# [?] Merge #7126: fix: crash when theme is changed if mnemonic dialog has been shown

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-06
Source: https://github.com/dashpay/dash/commit/7d0d5a7ea7ab6c71c47f048f58fa7cfe6b072509
Type: security-commit

## Details
Merge #7126: fix: crash when theme is changed if mnemonic dialog has been shown

009104c35916c02e89605ddde6375711851ec879 fix: return full functionality of Back / Cancel button on mnemonic verification dialog (Konstantin Akimov)
c24473b99d698b7a4c75b70f5b833824c5e23e96 fix: crash in mnemonicverificationdialog by proper using reject() event (Konstantin Akimov)

Pull request description:

  ## Issue being fixed or feature implemented
  First found by thepez while testing https://github.com/dashpay/dash/pull/7040

  It happens every time when create new wallet after dialog to validate mnemonic has been shown.

  Steps to reproduce:
   1. Create new wallet
   2. Show mnemonic
   3. Confirm the mnemonic is saved
   4. Close dialog by Canceling validation or by Confirming validation
   5. Change theme crashes app

  ```
      2025-12-22T15:16:31Z Posix Signal: Segmentation fault
      0#: (0x608F5BE3FDB5) stl_vector.h:115         - std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data::_M_copy_data(std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data const&)
       1#: (0x608F5BE3FDB5) stl_vector.h:127         - std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data::_M_swap_data(std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data&)
       2#: (0x608F5BE3FDB5) stl_vector.h:1962        - std::vector<unsigned long, std::allocator<unsigned long> >::_M_move_assign(std::vector<unsigned long, std::allocator<unsigned long> >&&, std::integral_constant<bool, true>)
       3#: (0x608F5BE3FDB5) stl_vector.h:771         - std::vector<unsigned long, std::allocator<unsigned long> >::operator=(std::vector<unsigned long, std::allocator<unsigned long> >&&)
       4#: (0x608F5BE3FDB5) stacktraces.cpp:784      - HandlePosixSignal
       5#: (0x7D6B37A45330) libc_sigaction.c         - ???
       6#: (0x608F5CC0951B) <unknown-file>           - ???
       7#: (0x608F5CC09901) <unknown-file>           - ???
       8#: (0x608F5B62369D) unique_lock.h:105        - std::unique_lock<std::recursive_mutex>::~unique_lock()
       9#: (0x608F5B62369D) sync.h:226               - UniqueLock<AnnotatedMixin<std::recursive_mutex> >::~UniqueLock()
      10#: (0x608F5B62369D) guiutil.cpp:1031         - GUIUtil::loadStyleSheet(bool)
      11#: (0x608F5B6243C4) guiutil.cpp:1616         - GUIUtil::loadTheme(bool)
      12#: (0x608F5B6C27B7) atomic_base.h:505        - std::__atomic_base<int>::load(std::memory_order) const
      13#: (0x608F5B6C27B7) qatomic_cxx11.h:239      - int QAtomicOps<int>::loadRelaxed<int>(std::atomic<int> const&)
      14#: (0x608F5B6C27B7) qbasicatomic.h:107       - QBasicAtomicInteger<int>::loadRelaxed() const
      15#: (0x608F5B6C27B7) qrefcount.h:66           - QtPrivate::RefCount::deref()
      16#: (0x608F5B6C27B7) qstring.h:1308           - QString::~QString()
```

_Trimmed to 38 lines — full report: https://github.com/dashpay/dash/commit/7d0d5a7ea7ab6c71c47f048f58fa7cfe6b072509_
