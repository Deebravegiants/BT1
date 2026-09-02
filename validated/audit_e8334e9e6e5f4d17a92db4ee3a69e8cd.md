## Analysis

The Rubicon report describes a case where an internal computation trusts a self-referential value (`_loopBorrowed`) that drifts away from the value that was actually validated/anchored, breaking an implicit invariant. The closest analog in this Ruby gem is a place where a piece of data that is *used* to make a security decision (which tenant/shop a message belongs to) is not the same data that is *covered by the cryptographic integrity check* (the HMAC). That is exactly the "bytes verified vs. bytes parsed/acted upon" analog category.

`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but `to_signable_string` — the data that is actually HMAC-verified — only returns the raw request body: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the signature only over `to_signable_string` (the body), never over the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers: [2](#0-1) 

`Registry.process` then forwards these unverified header values straight into the handler as the record of "which shop this data belongs to": [3](#0-2) 

The identity binding that is broken is:
`shop asserted to app handler (request.shop, from header)` ≠ `shop bound by the verified bytes (to_signable_string == raw_body only)`

Since headers are attacker-controlled on any HTTP request reaching the app's webhook endpoint, and only the body bytes are authenticated, an attacker who can obtain any one legitimately-signed `(body, hmac)` pair from Shopify — trivially available to any unprivileged user by installing the target app on their own store and triggering a webhook — can replay that exact `(body, hmac)` pair to the app's webhook route while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for an arbitrary victim shop domain. `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` hands the handler a `WebhookMetadata` claiming the (forged) victim shop, with attacker-supplied body content processed as if it came from that shop. This constitutes cross-tenant data injection into the app's webhook processing pipeline — no access token, `api_secret_key`, or privileged account required, only a legitimately-signed message the attacker obtained for their own tenant.

This does not require knowledge of the secret; it only requires knowledge of one legitimately-signed webhook payload+signature pair for any shop, which is available to any unprivileged internet user through normal app installation.

### Title
Webhook HMAC does not cover `shop-domain`/`topic` headers, allowing cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers. `HmacValidator.validate` verifies the HMAC exclusively against the body. `Webhooks::Registry.process` passes the unauthenticated `request.shop`/`request.topic` values to the app's handler as trusted tenant identity, so any `(body, hmac)` pair legitimately obtained for one shop can be replayed with a forged `shop-domain` header to make the gem report the webhook as belonging to a different shop.

### Finding Description
The equality that should hold is: `shop value the handler acts on == shop value covered by the HMAC-verified bytes`. In this gem it does not:

- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` come from headers: [4](#0-3) 
- `Request#to_signable_string` — the only data that is HMAC-checked — is just `@raw_body`: [5](#0-4) 
- `HmacValidator.validate_signature` computes/compares the HMAC solely over `to_signable_string`: [6](#0-5) 
- `Registry.process` trusts `request.shop`/`request.topic` unconditionally once the (body-only) HMAC check passes, and forwards them to the app-provided handler as the record of tenant identity: [3](#0-2) 

Because none of the identifying headers are part of the signed material, an attacker who possesses any single valid `(raw_body, x-shopify-hmac-sha256)` pair — trivially obtainable by installing the target app on their own Shopify store and letting Shopify deliver one real webhook — can send that exact body+signature to the app's webhook endpoint while freely rewriting `x-shopify-shop-domain` (and `x-shopify-topic`) to name a victim shop. The signature still validates because only the body is checked, and the gem reports the forged shop/topic to the handler as if authentic.

### Impact Explanation
This breaks the tenant identity boundary the gem is supposed to provide via `Webhooks::Registry.process`: an app's webhook handler that keys behavior/storage/session lookups off `WebhookMetadata#shop` (the documented and expected pattern) can be made to attribute attacker-controlled body content to an arbitrary victim shop, i.e. cross-tenant data injection/confusion — one of the explicitly in-scope Critical impacts (cross-tenant access).

### Likelihood Explanation
Likelihood is high for any app that uses this gem's webhook processing as documented: the attacker needs no secret, token, or privileged access — only the ability to install the target (public) app on a store they control and capture one webhook delivery, which is standard, unprivileged usage. No race condition or timing constraint is required, and the replay works indefinitely since none of the identity-bearing headers are re-validated.

### Recommendation
Include `shop-domain`, `topic`, `webhook-id`, and `api-version` in the HMAC-signed material (or otherwise cryptographically bind them, mirroring how Shopify's own webhook signing already covers headers/metadata in newer schemes), so `HmacValidator.validate` fails if any of these header values are altered. At minimum, document prominently that `request.shop`/`request.topic` are NOT authenticated by `Registry.process` and must not be trusted for tenant-sensitive decisions without independent verification (e.g., cross-checking against a shop known to have an active app installation/session).

### Proof of Concept
1. Attacker installs the target (public) Shopify app on their own store `attacker.myshopify.com` and triggers any webhook topic the app subscribes to; Shopify delivers a request with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's real `api_secret_key`.
2. Attacker captures `raw_body` and the valid `hmac` header from that delivery.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the identical `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against `hmac`: [7](#0-6) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `shop` is `"victim-shop.myshopify.com"` even though the data actually originated from, and was signed for, `attacker.myshopify.com`: [8](#0-7) 
6. Any app logic that trusts `data.shop` for tenant-scoped actions (storage keyed by shop, cache invalidation, order/customer sync, etc.) now operates under the wrong tenant's identity using attacker-controlled body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
