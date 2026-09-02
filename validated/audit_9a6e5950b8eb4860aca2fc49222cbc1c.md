### Title
Webhook HMAC only signs the request body, not the `shop` header — shop identity used for dispatch is unauthenticated - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `Utils::HmacValidator.validate` checks that signature. The `shop` (and `topic`/`webhook_id`) values are read from HTTP headers that are never included in the HMAC computation. `Registry.process` then dispatches the handler using this unauthenticated `shop` value, so the "shop the HMAC proves" and the "shop the app acts on" are two different, unbound things — the same class of bug as the report's callback-before-transfer flaw, where an action is performed on data that was never actually covered by the verification step that supposedly authorized it.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `Request#shop` is read straight from the (attacker-controllable, non-signed) `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` only calls `Utils::HmacValidator.validate(request)` and then immediately dispatches the handler using `request.shop`, which was never part of the signed material: [4](#0-3) 

Contrast this with the OAuth-callback `AuthQuery`, where `shop` **is** included in the signable string and therefore is bound by the HMAC: [5](#0-4) 

The identity binding broken: `shop authenticated by HMAC` (nothing, since HMAC covers only body bytes) ≠ `shop used as the routing/session key for the handler` (`request.shop`, taken from an unsigned header). Any party who can obtain one genuine, HMAC-signed webhook body/signature pair (e.g., by installing the app on their own shop and receiving legitimate webhooks) can replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint while substituting the `shop-domain` header for an arbitrary victim shop. `HmacValidator.validate` will still succeed because it never inspected the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability: an attacker who controls one tenant (their own installed shop) can cause the host application to process webhook data under a different, victim tenant's identity. Depending on how the host app's webhook handlers use `shop` (e.g., to select the merchant's session/access token, to write/delete data keyed by shop, or to trigger mandatory-webhook flows like `shop/redact`), this can lead to cross-tenant data corruption or disclosure — meeting the "Critical - cross-tenant access" bar defined in scope.

### Likelihood Explanation
Any user able to install the target app on a shop they control receives genuinely signed webhooks for that shop. Constructing the forged request (same raw body/HMAC, spoofed `shop-domain` header, sent directly to the app's webhook route rather than via Shopify) requires no secret material and no privileged access — only the gem's documented `Webhooks::Request`/`Registry.process` API surface, which explicitly does not bind the shop header to the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed material, or otherwise cryptographically bind them to the verified payload, so that `Utils::HmacValidator.validate` fails if any of these identity-relevant headers are altered from what Shopify actually sent.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; receive a legitimate webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `client_secret`).
2. Replay the request directly to the app's webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H`, but changing `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — this still matches `H`, so validation succeeds: [6](#0-5) 
4. The registered handler is invoked with `WebhookMetadata` where `shop == "victim.myshopify.com"`, even though the request was never authenticated as originating from that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
