### Title
Webhook `shop-domain` header is not covered by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC computed over the raw request body only, but the `shop` attribute that identifies which merchant/tenant the event belongs to is taken from an HTTP header that is never included in that HMAC. This breaks the identity binding `hmac_verifies(raw_body) == shop_attributed_to_event`, allowing an attacker who controls their own (free/dev) Shopify store to replay a genuinely-signed webhook body while forging the `shop-domain` header to impersonate a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` validates the webhook using `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` and HMACs it with the app's `api_secret_key`: [2](#0-1) [3](#0-2) 

Once the HMAC check passes, `Registry.process` immediately builds a `WebhookMetadata` using `request.shop`, which is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, not from anything covered by the signature: [4](#0-3) [5](#0-4) 

Because the HMAC only binds the byte content of the body, an attacker who legitimately owns a Shopify development store can trigger a real webhook for their own shop, capture the valid `(raw_body, hmac)` pair issued by Shopify for that event, and then replay that exact body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed because it only checks the body bytes against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event originated from the victim shop. This is the same class of bug as the report's inequality mismatch: two things that should be checked as equal (the entity the signature vouches for vs. the entity the application attributes the event to) are not actually bound together.

### Impact Explanation
If the app's webhook handlers use `WebhookMetadata#shop` to key data updates, access-control decisions, or trigger merchant-scoped side effects (common pattern for `shop/redact`, `customers/redact`, `customers/data_request`, order/product sync, etc.), this allows an attacker to inject attacker-controlled, but seemingly-authentic, event data attributed to an arbitrary victim shop — a cross-tenant confusion. This matches the Critical bucket in scope ("cross-tenant access").

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the app (or subscribe topics) on an attacker-owned Shopify store to obtain genuinely signed `(body, hmac)` pairs, and (2) the ability to POST directly to the app's public webhook endpoint with custom headers — both of which are available to any unprivileged internet user/merchant, with no access to the app's `api_secret_key` or any victim credentials required.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header into the signed material, or otherwise cross-check the header-derived shop against a value verified independently (e.g., look up the destination shop's own secret/session rather than trusting the header verbatim). At minimum, include the shop domain in `to_signable_string` so the HMAC computed by `HmacValidator` fails whenever the shop header is inconsistent with the originally signed request.

### Proof of Concept
1. Register a webhook topic (e.g., `orders/create`) for an app in a Shopify development store the attacker controls.
2. Trigger the event so Shopify sends a real webhook: `POST /webhooks` with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the attacker's own shop), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Capture `(B, H)`.
4. Replay: `POST /webhooks` to the same app endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only hashes `@raw_body`; `Registry.process` in `lib/shopify_api/webhooks/registry.rb` then calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data as if it came from the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
