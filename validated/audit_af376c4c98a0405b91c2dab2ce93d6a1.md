Confirmed: `VerifiableQuery` only requires `hmac` and `to_signable_string`, and for webhooks `to_signable_string` is defined as `@raw_body` alone [1](#0-0) , while `shop` is read from a separate, unsigned header [2](#0-1) . `Registry.process` validates the HMAC against the raw body only and then unconditionally trusts the header-derived `shop` value to build `WebhookMetadata` for the handler [3](#0-2) .

### Title
Webhook `shop` identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, never the `shop`, `topic`, or `webhook-id` headers. `HmacValidator.validate` therefore only proves that the *body* bytes were produced with the app's `client_secret`; it proves nothing about which shop the body belongs to. `Registry.process` nevertheless passes the unauthenticated `request.shop` value straight into `WebhookMetadata`, which host applications use to attribute the payload to a specific merchant record.

### Finding Description
The identity binding that should hold is:
```
shop claimed in WebhookMetadata == shop that the HMAC-signed body actually originated from
```
This binding is broken because the HMAC signature covers only `@raw_body` [1](#0-0) , while `shop` is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely independent of the signed bytes [2](#0-1) .

Critically, Shopify signs *all* webhooks for an app installation with the **same** `client_secret`/`api_secret_key`, regardless of which shop triggered the event [4](#0-3) . So a `(raw_body, hmac)` pair that is valid for shop A is *also* a valid pair for any other shop, because the header carrying the shop identity is never mixed into the signature computation.

`Registry.process` performs exactly one check — HMAC validity of the body — before dispatching to the handler with the header-derived shop:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

Before the attack: `shop` field trusted by the handler == shop where the signed body was legitimately generated.
After the attack: `shop` field trusted by the handler == arbitrary attacker-chosen value, while the signed body still legitimately originates from the attacker's own shop.

### Impact Explanation
This is a cross-tenant integrity break (Critical per the given rubric). An unprivileged internet user can install the app on their own free/trial Shopify store (a normal, unprivileged action), trigger any webhook topic the app subscribes to with content they control (e.g., product titles, order notes, customer fields), capture the resulting `(raw_body, hmac)` pair delivered to the app's webhook endpoint, then replay that exact body/HMAC pair to the same endpoint while substituting the `shop-domain` header with a victim shop's domain. Because the signature never covered the shop header, the request passes `HmacValidator.validate` and the host application's handler receives `WebhookMetadata` claiming the payload belongs to the victim shop. Any host application logic that uses `data.shop` to look up/update per-merchant state (inventory, orders, GDPR/customer records, billing, etc.) will act on attacker-controlled data under the victim's tenant identity — a cross-tenant access/injection vulnerability facilitated entirely by this gem's webhook verification primitive.

### Likelihood Explanation
Likelihood is high for any app that: (1) is public/installable by arbitrary merchants, and (2) subscribes to at least one webhook topic whose body an installer can influence (e.g. `products/create`, `orders/create` with custom metafields/notes, `customers/create`). Obtaining a valid signed webhook only requires installing the app on a store the attacker controls — no credential theft, TLS interception, or knowledge of `api_secret_key` is needed, satisfying the "unprivileged internet user" constraint.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop` header to the request before trusting it: e.g., include `topic`, `shop-domain`, and `webhook-id` headers in `to_signable_string` (matching Shopify's recommended verification which additionally checks header/body consistency), or require host apps to independently verify that `request.shop` corresponds to a shop that legitimately installed the app before processing, and reject/dedupe by `webhook_id` to prevent replay of a previously seen valid webhook under a different shop claim.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (unprivileged, self-service action).
2. Attacker performs an action that triggers a subscribed webhook topic with attacker-chosen content, e.g. creates a product with a malicious title/description.
3. Shopify delivers the webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and the raw JSON body.
4. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from this legitimate delivery (this is their own webhook traffic to their own endpoint — no third-party interception needed).
5. Attacker resends an HTTP POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
6. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= raw_body`) only, matches the supplied HMAC, and returns `true` [5](#0-4) .
7. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)`, causing the host application to process attacker-controlled data under the victim shop's tenant identity.

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
