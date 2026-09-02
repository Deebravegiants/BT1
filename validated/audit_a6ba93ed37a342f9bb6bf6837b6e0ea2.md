### Title
Webhook shop identity and topic are not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity by validating only the HMAC-SHA256 signature over the raw request body, while the shop identity (`shop-domain` header) and event topic (`topic` header) used to route and attribute the webhook are taken from unauthenticated HTTP headers that are never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop` and `Request#topic` are read straight from HTTP headers that are entirely outside that signed string: [2](#0-1) 

`Registry.process` verifies the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it against `verifiable_query.hmac`: [3](#0-2) 

After this check passes, `Registry.process` immediately trusts `request.shop` and `request.topic` — both unauthenticated header values — to build `WebhookMetadata` and dispatch to the registered handler: [4](#0-3) 

The binding that should hold is:
`bytes_verified_by_HMAC == bytes_used_to_identify_the_tenant_and_topic`

Here, `bytes_verified_by_HMAC = raw_body` while `bytes_used_to_identify_tenant/topic = shopify-shop-domain header, shopify-topic header`. These are disjoint, so the equality is broken: the signature says nothing about which shop or which topic the body belongs to.

Because the HMAC secret (the app's `client_secret`) is shared across every shop that installs the app, any shop that installs the app receives its own webhooks with a valid HMAC over the raw body. Nothing in the request payload itself binds it to a shop or topic — that binding exists only in the unsigned headers. An unprivileged actor who has installed the app on their own store (a routine, self-service action requiring no special privilege) can capture one of their own legitimately-signed webhook deliveries (valid HMAC, since it was genuinely sent by Shopify for their shop) and replay it to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` headers to point at a different (victim) shop or a different, more sensitive topic (e.g., `customers/redact`, `shop/redact`). `Registry.process` will still consider the HMAC valid (it only checks the body) and will hand the attacker's `WebhookMetadata` — carrying attacker-controlled body content but the victim's `shop` — straight to the host application's handler.

### Impact Explanation
This breaks the shop/topic identity binding that host applications rely on to attribute webhook data to the correct tenant. A host app trusts `WebhookMetadata#shop` (sourced from this gem) as the authoritative tenant identifier once `Registry.process` has accepted the HMAC. An attacker can forge webhook deliveries that are processed as if they originated from an arbitrary victim shop, or can relabel a payload's topic to route attacker-controlled body content into a differently-behaving handler (e.g., mandatory GDPR redact handlers). This is a cross-tenant confusion vulnerability rooted entirely in this gem's `Request`/`Registry` design — the gem is the component responsible for asserting "this body, with this HMAC, belongs to this shop and this topic," and it fails to make that assertion.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the target app on a shop the attacker controls (standard, unprivileged, self-service action for any Shopify app that supports public installs), (2) capturing one legitimately-delivered webhook to that shop (trivial via a controlled endpoint), and (3) replaying it to the app's webhook endpoint with modified `shop-domain`/`topic` headers. No access token, `client_secret`, or privileged credential is required.

### Recommendation
Include the shop domain and topic (and any other header claims that are trusted downstream) in the HMAC-signed material verified by `Utils::HmacValidator`, or otherwise cryptographically bind these header values to the payload before `Registry.process` trusts them (for example, requiring `WebhookMetadata#shop` to be validated against a shop the host app has resolved through an authenticated channel, or, if Shopify's webhook signing genuinely only ever covers the raw body, requiring the host app to independently authenticate `shop`/`topic` before dispatch, and documenting this gap explicitly in `Registry.process`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, unprivileged).
2. Shopify sends a legitimate webhook (e.g., `orders/create`) to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the raw JSON body using the shared `client_secret`.
3. Attacker captures the raw body and its valid HMAC header.
4. Attacker replays the exact same raw body + HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally changes `X-Shopify-Topic` to `customers/redact` or `shop/redact`).
5. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds because it only checks `raw_body` against the HMAC.
6. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied header values and dispatches to the registered handler as if the (forged) shop and topic were authentic.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
