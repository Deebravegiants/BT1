### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC validation performed by `Registry.process` verifies the request *body* only, while `request.shop` — the value used to attribute the webhook to a tenant — is read from an HTTP header that is completely outside the signed content.

### Finding Description
`Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes the signature over `request.to_signable_string`. That method returns only the raw body: [2](#0-1) . Meanwhile `request.shop` — the tenant identifier passed straight into `WebhookMetadata` and handed to the app's handler — is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed bytes: [3](#0-2) [4](#0-3) .

This breaks the identity binding `HMAC-verified bytes == bytes acted upon`: the equality that should hold is `hmac_signed_content ⊇ {shop, topic, body}`, but here `hmac_signed_content = {raw_body}` while `{shop, topic, webhook_id}` are taken from unauthenticated headers. Anyone who obtains one valid `(raw_body, hmac)` pair — e.g. from their own shop's webhook delivery, since a merchant that installs the app receives a legitimately signed webhook for their own shop — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header for a different, victim shop. `HmacValidator.validate` only recomputes the HMAC over `raw_body` [5](#0-4) , so the forged header passes validation unchanged, and the handler executes believing the payload originated from the victim shop.

### Impact Explanation
If a host application's `WebhookHandler#handle` implementation uses `data.shop` to select which tenant's data/session to operate on (the documented and intended use of `WebhookMetadata#shop`), an attacker can cause the app to apply another shop's webhook body under a victim shop's identity, or attribute their own crafted-looking payload to an arbitrary target shop domain. This is a cross-tenant confusion at the trust boundary the gem is supposed to enforce (HMAC-authenticated shop identity), matching the "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires only: (1) becoming an app-installed merchant capable of triggering at least one real webhook delivery for their own shop (a standard, unprivileged action), and (2) replaying that raw body with a swapped shop-domain header to the app's public webhook endpoint. No access to `client_secret`, access tokens, or the target shop's credentials is required, since the header being modified is never part of the signature.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed content check, or independently verify that `request.shop` corresponds to a shop with a valid, provisioned session/installation before dispatching to the handler. At minimum, document and/or enforce that `WebhookMetadata#shop` must not be trusted as an authenticated value unless cross-checked against stored session state.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook delivery: body `B`, header `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and matches `H` — validation succeeds despite the header being attacker-controlled [6](#0-5) .
4. `handler.handle` is invoked with `WebhookMetadata.new(... shop: request.shop ...)` set to `"victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-controlled content under the victim tenant's identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
