### Title
Webhook `shop` identity is not covered by the HMAC, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw request body, while `shop` (the tenant identifier passed down to the application's webhook handler) is read straight from an HTTP header that is never included in the HMAC computation. Anyone who can obtain one genuine, correctly-signed webhook payload (e.g. by legitimately installing the app on their own store) can replay that exact body+HMAC pair to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop, and the library will accept it as authentic and hand the attacker-chosen `shop` to the handler.

### Finding Description
`HmacValidator.validate` verifies a request by recomputing the HMAC over whatever `to_signable_string` returns and comparing it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled from headers that are completely outside the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity that is forwarded to the application's handler via `WebhookMetadata`: [4](#0-3) 

This breaks the identity binding: `HMAC-verified(payload)` ⇒ "this body was produced by an entity holding `api_secret_key`", but the code implicitly treats it as ⇒ "this body, *for this shop*, was produced by that entity." Because `api_secret_key` is a single app-level secret shared across every shop that installs the app, any shop's genuine webhook payload is valid for every other shop's tenant context as far as this gem's verification logic is concerned. An attacker only needs to be an ordinary merchant who installs the public app on their own shop (no elevated privilege, no knowledge of `api_secret_key` required) to obtain one valid `(raw_body, x-shopify-hmac-sha256)` pair, then POST it to the app's public webhook endpoint with `x-shopify-shop-domain` swapped to the victim's domain.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to select which merchant's data/session the webhook payload applies to (the documented and expected use of this field), an attacker can inject data/events that the application will process as if they originated from a different, victim tenant — i.e., cross-tenant access/data injection using only a replayed, unmodified payload they legitimately received for their own shop. This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Medium-to-High: the attacker only needs normal, unprivileged access to install/use the app on any store to receive a real signed webhook, then can freely forge the `shop-domain` header on a direct POST to the app's known webhook URL — no secret material or elevated access is needed.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically tie `shop` to the verified payload — e.g. reject/flag webhooks where the shop domain in the header cannot be corroborated against a per-shop registration record, or require verification that the specific shop is one the app is actually installed on for the specific webhook subscription id before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted for tenant selection without an additional binding check.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com` and triggers any subscribed webhook event (e.g. `orders/create`), legitimately receiving `raw_body` and header `x-shopify-hmac-sha256: H`, both valid.
2. Attacker sends a new POST to the app's public webhook endpoint with the same `raw_body` and same `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only (`request.rb:36-38`) and succeeds, since the header was never part of the signed string.
4. `Registry.process` (`registry.rb:188-199`) accepts the request and calls the handler with `shop: "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
