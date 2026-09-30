# [?] wallet: fix deadlock in on_event_adb_added_verified_tx

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2023-01-12
Source: https://github.com/spesmilo/electrum/commit/8829b7cd632aeca56d21ee109f4030092052af62
Type: security-commit

## Details
wallet: fix deadlock in on_event_adb_added_verified_tx

wallet.lock -> wallet.transaction_lock order must be respected.

deadlock example:
```
# ThreadID: 19100
File: ...\Python\Python310\lib\threading.py", line 966, in _bootstrap
  self._bootstrap_inner()
File: ...\Python\Python310\lib\threading.py", line 1009, in _bootstrap_inner
  self.run()
File: ...\Python\Python310\lib\threading.py", line 946, in run
  self._target(*self._args, **self._kwargs)
File: "...\electrum\electrum\util.py", line 1552, in run_event_loop
  loop.run_until_complete(stopping_fut)
File: ...\Python\Python310\lib\asyncio\base_events.py", line 633, in run_until_complete
  self.run_forever()
File: ...\Python\Python310\lib\asyncio\windows_events.py", line 321, in run_forever
  super().run_forever()
File: ...\Python\Python310\lib\asyncio\base_events.py", line 600, in run_forever
  self._run_once()
File: ...\Python\Python310\lib\asyncio\base_events.py", line 1896, in _run_once
  handle._run()
File: ...\Python\Python310\lib\asyncio\events.py", line 80, in _run
  self._context.run(self._callback, *self._args)
File: "...\electrum\electrum\wallet.py", line 494, in on_event_adb_added_verified_tx
  self._update_invoices_and_reqs_touched_by_tx(tx_hash)
File: "...\electrum\electrum\wallet.py", line 2454, in _update_invoices_and_reqs_touched_by_tx
  status = self.get_invoice_status(request)
File: "...\electrum\electrum\wallet.py", line 2333, in get_invoice_status
  paid, conf = self.is_onchain_invoice_paid(invoice)
File: "...\electrum\electrum\wallet.py", line 1120, in is_onchain_invoice_paid
  is_paid, conf_needed, relevant_txs = self._is_onchain_invoice_paid(invoice)
File: "...\electrum\electrum\wallet.py", line 1095, in _is_onchain_invoice_paid
  with self.lock, self.transaction_lock:
File: "...\electrum\electrum\address_synchronizer.py", line 70, in acquire
  return self._lock.acquire(*args, **kwargs)

# ThreadID: 20040
File: "C:\Program Files\JetBrains\PyCharm Community Edition 2021.3.3\plugins\python-ce\helpers\pycharm\_jb_pytest_runner.py", line 51, in <module>
  sys.exit(pytest.main(args, plugins_to_load + [Plugin]))
File: "...\Python\Python310\site-packages\_pytest\config\__init__.py", line 164, in main
  ret: Union[ExitCode, int] = config.hook.pytest_cmdline_main(
File: ...\Python\Python310\lib\site-packages\pluggy\_hooks.py", line 265, in __call__
  return self._hookexec(self.name, self.get_hookimpls(), kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_manager.py", line 80, in _hookexec
  return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_callers.py", line 39, in _multicall
  res = hook_impl.function(*args)
File: "...\Python\Python310\site-packages\_pytest\main.py", line 315, in pytest_cmdline_main
  return wrap_session(config, _main)
File: "...\Python\Python310\site-packages\_pytest\main.py", line 268, in wrap_session
  session.exitstatus = doit(config, session) or 0
File: "...\Python\Python310\site-packages\_pytest\main.py", line 322, in _main
  config.hook.pytest_runtestloop(session=session)
File: ...\Python\Python310\lib\site-packages\pluggy\_hooks.py", line 265, in __call__
  return self._hookexec(self.name, self.get_hookimpls(), kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_manager.py", line 80, in _hookexec
  return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_callers.py", line 39, in _multicall
  res = hook_impl.function(*args)
File: "...\Python\Python310\site-packages\_pytest\main.py", line 347, in pytest_runtestloop
  item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
File: ...\Python\Python310\lib\site-packages\pluggy\_hooks.py", line 265, in __call__
  return self._hookexec(self.name, self.get_hookimpls(), kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_manager.py", line 80, in _hookexec
  return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_callers.py", line 39, in _multicall
  res = hook_impl.function(*args)
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 111, in pytest_runtest_protocol
  runtestprotocol(item, nextitem=nextitem)
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 130, in runtestprotocol
  reports.append(call_and_report(item, "call", log))
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 219, in call_and_report
  call = call_runtest_hook(item, when, **kwds)
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 258, in call_runtest_hook
  return CallInfo.from_call(
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 338, in from_call
  result: Optional[TResult] = func()
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 259, in <lambda>
  lambda: ihook(item=item, **kwds), when=when, reraise=reraise
File: ...\Python\Python310\lib\site-packages\pluggy\_hooks.py", line 265, in __call__
  return self._hookexec(self.name, self.get_hookimpls(), kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_manager.py", line 80, in _hookexec
  return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
File: ...\Python\Python310\lib\site-packages\pluggy\_callers.py", line 39, in _multicall
  res = hook_impl.function(*args)
File: "...\Python\Python310\site-packages\_pytest\runner.py", line 166, in pytest_runtest_call
  item.runtest()
File: "...\Python\Python310\site-packages\_pytest\unittest.py", line 327, in runtest
  self._testcase(result=self)  # type: ignore[arg-type]
File: ...\Python\Python310\lib\unittest\case.py", line 650, in __call__
  return self.run(*args, **kwds)
File: ...\Python\Python310\lib\unittest\case.py", line 591, in run
  self._callTestMethod(testMethod)
File: ...\Python\Python310\lib\unittest\case.py", line 549, in _callTestMethod
  method()
File: "...\electrum\electrum\tests\test_invoices.py", line 120, in test_wallet_without_ln_creates_payreq_and_gets_paid_onchain
  self.assertEqual(PR_PAID, wallet1.get_invoice_status(pr))
File: "...\electrum\electrum\wallet.py", line 2333, in get_invoice_status
  paid, conf = self.is_onchain_invoice_paid(invoice)
File: "...\electrum\electrum\wallet.py", line 1120, in is_onchain_invoice_paid
  is_paid, conf_needed, relevant_txs = self._is_onchain_invoice_paid(invoice)
File: "...\electrum\electrum\wallet.py", line 1095, in _is_onchain_invoice_paid
  with self.lock, self.transaction_lock:
File: "...\electrum\electrum\address_synchronizer.py", line 70, in acquire
  return self._lock.acquire(*args, **kwargs)
```

## Patch
### electrum/wallet.py
```diff
@@ -2440,7 +2440,7 @@ def _update_invoices_and_reqs_touched_by_tx(self, tx_hash: str) -> None:
         if tx is None:
             return
         relevant_invoice_keys = set()
-        with self.transaction_lock:
+        with self.lock, self.transaction_lock:
             for txo in tx.outputs():
                 addr = txo.address
                 if request:=self.get_request_by_addr(addr):
```
