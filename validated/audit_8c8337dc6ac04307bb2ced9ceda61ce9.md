I found a genuine analog. The bug-class from the report (an identity field used to act on behalf of a party, but not included in the cryptographic validity check) maps directly onto how this gem validates webhook requests.

### Title
Webhook shop-domain identity spoofing via HMAC that only covers the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the `X-Shopify-Hmac-Sha256` signature verified by `HmacValidator` proves nothing about the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers. Yet `Registry.process` trusts `request.shop` (parsed straight from the unauthenticated header) as the tenant identity dispatched to the app's webhook handler.

### Finding Description
`Registry.process` validates a webhook solely with: [1](#0-0) 

The HMAC check itself, `Utils::HmacValidator.validate`, computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — none of the identity headers are folded into the signed material: [3](#0-2) 

`shop`, `topic`, `webhook_id`, and `api_version` are all parsed from unauthenticated headers and then handed to the handler as trusted tenant context: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop header == shop cryptographically bound to the signed payload`. Because only the body is signed, this equality never gets checked — the gem accepts any `shop-domain` header alongside a body/HMAC pair that was genuinely produced for a *different* shop.

### Impact Explanation
An attacker who is a legitimate merchant/installer of the app (i.e., controls their own shop and can trigger a real webhook delivery to the app, e.g. `orders/create`) captures one genuine `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`. They then replay that exact body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and optionally `X-Shopify-Topic`/`webhook-id`) with a victim shop's domain. `HmacValidator.validate` still returns `true`, because the signature only ever covered the raw body bytes, and `WebhookMetadata.shop` is populated with the attacker-chosen victim domain. Any host application that uses `request.shop` from this gem to look up per-tenant sessions/data (the documented usage pattern) will process attacker-controlled data as coming from a different tenant — a cross-tenant identity confusion achieved without ever needing the app's `client_secret`, an access token, or the victim's credentials.

### Likelihood Explanation
Any user who can install the app on a shop they control (the normal path for any Shopify app, including free/trial installs) can obtain a legitimately-signed webhook body/HMAC pair for their own tenant, then simply resend it with an altered domain header. No secret material or victim interaction is required, making this straightforward for anyone able to reach the app's public webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material used by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the payload before dispatch, so a body signed for one shop cannot be replayed under a different shop's identity.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., create an order) to receive a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify.
2. Resend that exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and adjust `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if desired).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC — as shown in `lib/shopify_api/webhooks/request.rb:36-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop == "victim.myshopify.com"`, even though the payload was never produced for that shop.

### Citations

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
