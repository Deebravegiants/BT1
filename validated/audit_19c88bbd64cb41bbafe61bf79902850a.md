This is the critical finding: in `ShopifyAPI::Webhooks::Request`, the HMAC only signs the raw request body (`to_signable_string` returns `@raw_body`), while `shop` (`shop-domain` header), `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers, entirely outside the HMAC computation. [1](#0-0) 

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant spoofing in webhook processing - (File: lib/shopify_api/utils/verifiable_query.rb / lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is validated against `to_signable_string`, which returns only `@raw_body`. The `shop` value, however, is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header via `shopify_header("shop-domain")`, a field that is never included in the signed bytes. Any attacker who obtains one legitimate HMAC over a given raw body (e.g. by replaying a genuine webhook delivery, or by any means where the raw body/HMAC pair is observable) can resend that exact body+HMAC pair while substituting an arbitrary `shop-domain` header value, and `ShopifyAPI::Utils::HmacValidator.validate` will report success because it only checks `OpenSSL.secure_compare(computed_signature, hmac)` against `raw_body` bytes. [2](#0-1) 

### Finding Description
The identity binding broken here is: **`shop` field trusted by the handler == `shop` field covered by the HMAC**. This equality fails.

- `HmacValidator.validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string`.
- For `Webhooks::Request`, `to_signable_string` is `@raw_body` only — it does not incorporate `shop`, `topic`, `webhook_id`, or `api_version`.
- `Webhooks::Request#shop` is sourced straight from the HTTP header (`shopify_header("shop-domain")`), which is attacker-controllable input in any request the attacker crafts and sends to the app's webhook endpoint.
- `Registry.process` (per `test/webhooks/registry_test.rb`) calls handlers passing `data.shop` derived from this unauthenticated header, and app code (per `docs`) is expected to use `data.shop` to identify which merchant/tenant the webhook data belongs to.

This mirrors the RubiconRouter bug class: an identity value that is *acted upon* (there, `offer.owner`/cancel authorization; here, the tenant/shop identity used to route webhook data) is not the value that is *cryptographically bound* by the security check (there, `msg.sender` vs `offer.owner` set by a different contract; here, `shop` header vs the HMAC-covered `raw_body`).

### Impact Explanation
An attacker who can obtain any single valid `(raw_body, hmac)` pair — e.g., a body that legitimately reaches the app (even for their own store, since anyone can create a store and receive real webhooks for it) — can replay that exact byte-identical body with a forged `x-shopify-shop-domain` header claiming to be a *different* merchant's shop. Because `HmacValidator.validate` never fails (the raw body is unchanged and its HMAC is still valid), `Registry.process` will invoke the registered handler with `data.shop` set to the attacker-chosen shop while carrying the attacker's own (valid, non-secret) body content. If the host application uses `data.shop` to look up per-tenant state, apply the payload to a specific merchant's records, or make decisions that trust the shop identity without additional binding, this results in a cross-tenant write/desync — data intended for shop A processed under shop B's identity.

### Likelihood Explanation
Likelihood requires the attacker to first obtain a legitimate `(body, hmac)` pair, which is achievable without any privileged credentials: the attacker can create their own free Shopify development store, install the target app (or trigger a compatible webhook topic), and capture that store's own genuine webhook HMAC + raw body — no access token or `client_secret` is needed. They then replay it directly to the target app's public webhook endpoint with a spoofed `shop-domain` header. This satisfies the "unprivileged internet user" constraint and does not require TLS interception, leaked secrets, or social engineering.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signature — e.g., verify `shop` against session/tenant lookup keyed by a value that is itself signed, rather than trusting the raw header. At minimum, document that `Webhooks::Request#shop` is unauthenticated and must not be used by host applications as a trusted tenant identifier without separate verification (e.g., cross-checking against the shop associated with the currently registered webhook subscription id).

### Proof of Concept
1. Attacker creates their own Shopify dev store `attacker-shop.myshopify.com`, installs the target app, and triggers a webhook (e.g. `orders/create`) so Shopify sends a genuine webhook to the app's endpoint with a valid `raw_body` and `x-shopify-hmac-sha256` computed over that body with the app's `client_secret` — attacker does not need to know the secret, they just capture the delivered `(raw_body, hmac)` pair from their own store's traffic.
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, per [3](#0-2) , which only checks the raw body's signature and succeeds.
4. The registered handler is invoked with `data.shop == "victim-shop.myshopify.com"` even though the body's HMAC was never computed with reference to that shop, per [4](#0-3) , causing the app to process attacker-controlled webhook content under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
