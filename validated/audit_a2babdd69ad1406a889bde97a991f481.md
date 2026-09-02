## Title
Webhook shop identity spoofing via `X-Shopify-Shop-Domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook signature verification in this gem only covers the raw request body, not the `shop-domain` header that the gem uses to identify which tenant a webhook belongs to. Because a single app-level `api_secret_key` is used to sign webhooks for *every* shop that has installed the app, an attacker who controls (or has installed) one shop on the app can capture a legitimate, validly-signed webhook and replay it against the app's webhook endpoint with a forged `X-Shopify-Shop-Domain`/`shopify-shop-domain` header pointing at a victim shop. `ShopifyAPI::Webhooks::Registry.process` will accept the HMAC as valid and dispatch the handler with the attacker-chosen `shop`, breaking the binding between the authenticated bytes and the shop identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from a header that is never included in the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` against the HMAC, i.e., only the body: [3](#0-2) 

`Registry.process` trusts this validation and then forwards `request.shop` — the unauthenticated header — straight to the app's handler as the tenant identity: [4](#0-3) 

Because Shopify webhooks for a given app are all signed with the same `api_secret_key` regardless of which shop sent them, any shop that installs the app (including an attacker-owned shop) can obtain a genuinely-signed `(body, hmac)` pair. Since the `shop-domain` header is not part of the signed bytes, that pair remains valid HMAC-wise no matter what shop-domain header is attached to the replayed request. An attacker can therefore submit the captured body+HMAC to the app's webhook endpoint with the header rewritten to a victim shop's domain, and `Registry.process` will treat it as an authentic webhook `for the victim shop`, invoking the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `shop` is attacker-controlled.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality the code implicitly assumes is `hmac_valid(body) == shop_header_is_authentic`, but in reality `hmac_valid(body)` only proves the body came from *some* installed shop of this app, not that it came from the shop named in the header.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to key persistence, authorization, or business logic (the intended and documented usage pattern) can be made to process attacker-supplied webhook payloads under a victim shop's identity — a cross-tenant access primitive. Depending on the webhook topic replayed (e.g., `app/uninstalled`, `shop/update`, `customers/data_request`, order/customer webhooks), this can lead to corruption of another merchant's stored data, unauthorized state changes, or disclosure/mutation of another tenant's records — a cross-tenant access impact.

### Likelihood Explanation
The only prerequisite is that the attacker's own shop (or any shop they can trigger webhooks from) has the app installed — no special privilege, no access token, and no `api_secret_key` knowledge is required, since the attacker relies on genuinely-issued webhooks for their own shop. Replaying an HTTP request with a modified header is trivial once a legitimate webhook has been captured.

### Recommendation
Bind the shop identity into the verified material, e.g. include `shop-domain` (and ideally `webhook-id`, `topic`, `api-version`) in the HMAC-signed data validated by `HmacValidator`, or independently verify that the `shop-domain` header value belongs to a shop actually authorized for the received `api_secret_key`/app installation before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., updates a product) and captures the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since it's a real webhook from Shopify using the app's shared secret).
3. Attacker replays the exact same body `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` against `H`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `shop: "victim-shop.myshopify.com"`, causing the app to act on data intended for the attacker's own shop as if it belonged to the victim.

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
