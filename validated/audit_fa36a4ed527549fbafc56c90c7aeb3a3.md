### Title
Webhook shop identity spoofing via HMAC-body-only verification — cross-tenant webhook confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (tenant identity) is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed content. `Webhooks::Registry.process` trusts this unverified header value to attribute the webhook payload to a tenant when invoking the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from a header that is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes/compares the signature strictly against `to_signable_string` (the body), so it never covers the `shop-domain` header value: [3](#0-2) 

`Webhooks::Registry.process` accepts a request once `HmacValidator.validate` passes and then forwards `request.shop` — the unauthenticated header — as the tenant identity to the app's handler: [4](#0-3) 

This breaks the identity binding: `hmac_verifies(body)` ≠ `hmac_verifies(body, shop)`. The equality the code implicitly assumes — "the shop whose secret validated this HMAC" == "the shop named in the `shop-domain` header" — does not hold, because the header is excluded from the signed bytes.

### Impact Explanation
An attacker who can reach the app's public webhook endpoint (no Shopify credentials, access token, or `client_secret` required) and who possesses any single previously-observed valid `(raw_body, hmac)` pair for the app (webhook deliveries are plain HTTP POSTs an attacker who controls a network path, a logging proxy, or simply captures their own store's webhook can obtain) can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` will hand the payload to the app's handler tagged as if it came from the attacker-chosen shop. Depending on how the host app keys its data store by `WebhookMetadata#shop` (the documented and expected use per `docs/usage/webhooks.md`), this enables cross-tenant data confusion/injection — e.g., writing or overwriting another merchant's order/product/customer records with attacker-supplied content, without ever needing that merchant's credentials.

### Likelihood Explanation
Any unprivileged actor with network access to the app's webhook endpoint and one legitimately-captured `(body, hmac)` sample from any shop (including their own trial/dev store) can construct the spoofed request; no secret material of the target shop or app is needed. This is a straightforward, deterministic bypass of the shop-identity binding, not a race condition or probabilistic bug.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the HMAC-signed content, or otherwise cryptographically bind them to the verified payload, before trusting `request.shop` in `Registry.process`. At minimum, `to_signable_string` should incorporate the `shop-domain` header so `HmacValidator.validate` fails whenever it is altered independently of the body.

### Proof of Concept
1. Capture one legitimate webhook delivery to the app: raw JSON body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's `client_secret`), originally sent with `X-Shopify-Shop-Domain: victim-or-attacker-shop.myshopify.com`.
2. Replay the same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but set `X-Shopify-Shop-Domain: other-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only, matches `H`, and returns `true`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) proceeds and calls the handler with `WebhookMetadata.new(shop: "other-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process/store `B`'s content under the wrong tenant.

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
