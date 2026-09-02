## Title
Webhook shop/topic identity fields are not covered by the HMAC signature, enabling cross-tenant replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the request body only, then dispatches to the handler using `shop`, `topic`, `webhook_id`, and `api_version` values that are read straight from HTTP headers and are never included in the HMAC computation. An attacker who has captured one legitimately-signed webhook body/HMAC pair for a shop they control can replay that exact (body, HMAC) pair while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header, and the signature check still passes, since the secret and body haven't changed. This is the same bug class described in the report: a value (`shop`) is acted upon by the application but never bound by the cryptographic check meant to authenticate the request.

### Finding Description
`Request#hmac` computes the signable value strictly from the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled from headers with no relationship to the signed content: [2](#0-1) 

`Registry.process` validates only that the HMAC matches the body, then immediately trusts `request.topic` and `request.shop` to dispatch the handler and construct `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate` only ever compares `verifiable_query.hmac` against a signature computed over `verifiable_query.to_signable_string`, which for `Request` is just `@raw_body`: [4](#0-3) 

The identity binding that should hold is:
`shop_header == shop_covered_by_hmac`

but in reality:
`shop_header (attacker-controlled) != anything covered by HMAC (only raw_body is covered)`

Because the app's `api_secret_key` is a single shared secret used across every shop that installs the app (it is not per-shop), any body+HMAC pair that was validly generated for one shop remains a validly signed pair regardless of which `x-shopify-shop-domain` header accompanies it. An attacker can install the app on a shop they control (a normal, unprivileged, self-service action requiring no special credentials), capture one genuine webhook delivery (body + `x-shopify-hmac-sha256` header), and replay that exact HTTP request to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. `HmacValidator.validate` will still return `true`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the body belongs to the victim shop.

### Impact Explanation
Downstream host applications (e.g., using this gem per its own documented webhook handler pattern) rely on `WebhookMetadata#shop` to determine which tenant's data/session to use when processing the payload. Because the shop identity is never authenticated, this allows cross-tenant data injection/confusion — an attacker can cause data associated with their own store's webhook body to be processed under a victim shop's identity, and can potentially also fabricate the `topic` header for the same replayed body, causing the handler registered for a different topic to run on data it did not expect. This matches the Critical "cross-tenant access" impact criterion: the binding between the authenticated payload and the tenant it is attributed to is broken.

### Likelihood Explanation
Exploitation requires no leaked credentials, no access token, and no privileged account: an attacker only needs to (1) install the target app on a shop they control (a free, self-service action any developer can perform) to obtain one genuine `(raw_body, hmac)` pair, and (2) send an HTTP POST to the app's public webhook endpoint with that exact body/HMAC but a forged `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header. This is entirely reachable through the gem's own webhook verification path (`ShopifyAPI::Webhooks::Registry.process` / `HmacValidator.validate`), not dependent on the host app ignoring documentation — the gem's `HmacValidator` genuinely never covers these header fields.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, at minimum) in the HMAC-covered signable content, or otherwise cryptographically bind them to the payload (e.g., verify `shop` against the shop associated with the currently active/known session prior to trusting it, or require the caller to separately confirm the shop is one the app is actually installed on before processing). At minimum, `Request#to_signable_string` should not silently omit fields that `Registry.process` and downstream handlers treat as trusted identity data.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and receive one legitimate webhook delivery, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: ...
   Body: {"id":123,...}
   ```
2. Capture the raw body and the `x-shopify-hmac-sha256` value.
3. Replay the identical body and HMAC header to the same endpoint, but change:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb`, only `@raw_body` is checked), and `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload actually originated from, and was only ever authenticated for, `attacker-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
