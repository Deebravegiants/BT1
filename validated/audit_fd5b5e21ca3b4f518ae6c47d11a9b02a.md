### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, but the `shop` identity field used downstream to dispatch tenant-specific work is taken from an HTTP header that is never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `#shop` is read directly, unauthenticated, from the `x-shopify-shop-domain`/`shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The `HmacValidator.validate` / `validate_signature` methods compute the signature exclusively from `verifiable_query.to_signable_string`, i.e. the body — the `shop`, `topic`, `api-version`, and `webhook-id` headers are excluded from the signed data: [4](#0-3) 

The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_which_shop's_data_is_processed`. Here that equality breaks: the HMAC only binds the body, while `shop` (the tenant selector consumed by `WebhookMetadata.shop` and forwarded to the handler) is an unsigned, attacker-influenceable header value: [5](#0-4) 

Because `api_secret_key` is the app's single `client_secret`, shared across every shop that has installed the app, a valid HMAC over a given body only proves "this body/HMAC pair was produced with this app's secret" — it does not prove which shop the event belongs to. An operator of shop A (a legitimately installed, unprivileged tenant) can trigger events that cause Shopify to emit a validly-HMAC-signed webhook with attacker-chosen body content (e.g., putting arbitrary text into a product title, tag, or order note that gets echoed into the webhook payload) and then present that same (body, hmac) pair to the app's webhook endpoint while claiming an arbitrary `x-shopify-shop-domain` value. `Registry.process` will accept it, because `Utils::HmacValidator.validate` only checks the body, and the handler receives `WebhookMetadata.shop` set to whatever shop domain the attacker put in the header.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` to select the merchant record, session, or access token to act on (a common and expected pattern, since the metadata is documented as identifying the shop for the event), an attacker can cause data belonging to, or actions performed against, a victim shop's session/token to be triggered using attacker-controlled event content — a cross-tenant access primitive. This matches the Critical impact category (cross-tenant access) allowed by the rules, because the tenant boundary (which shop's token/session the app should act with) is defined by an unauthenticated field.

### Likelihood Explanation
Exploitation only requires an unprivileged attacker who has installed the app on their own shop (a normal condition for any multi-tenant Shopify app) — no leaked secrets, no privileged access, and no interaction with `api_secret_key` itself is required, satisfying the in-scope constraints of the rules. The attacker needs the ability to observe or predict the raw webhook body (achievable since webhook payloads for common topics like `orders/create`/`products/update` are largely attacker-controlled data from their own store) and to replay it to the app's public webhook endpoint with a modified `shop-domain` header.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values in the HMAC-signed material, or, at minimum, have `ShopifyAPI::Webhooks::Registry.process` cross-check `request.shop` against a known/registered set of shops for the app (e.g., verifying an existing session exists for that shop) before constructing `WebhookMetadata` and invoking the handler. Document clearly that `Request#shop` is unauthenticated so host applications do not use it as a trust boundary without additional verification.

### Proof of Concept
1. App has two installed shops: `victim.myshopify.com` and `attacker.myshopify.com`, sharing the app's single `api_secret_key`.
2. Attacker triggers a real webhook event on their own store (e.g., updates a product with a crafted title/body) so Shopify sends a webhook to the app's endpoint with a body `B` and a correctly computed `hmac-sha256` header `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker (or anyone able to reach the app's public webhook endpoint) resends a POST to that endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
