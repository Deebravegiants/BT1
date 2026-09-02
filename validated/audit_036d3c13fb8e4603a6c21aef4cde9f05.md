### Title
Webhook Shop-Domain Spoofing via HMAC Not Binding the `shop` Header - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, then trusts the `shop` value taken from the unsigned `x-shopify-shop-domain` HTTP header when constructing `WebhookMetadata` passed to the app's handler. Because the shared `api_secret_key` used to compute the HMAC is the same for every shop that has installed the app, and the `shop` field is never part of the HMAC-signed content, an attacker who legitimately triggers a webhook for their own (attacker-controlled) shop can capture a valid `(body, hmac)` pair and replay it against the app's public webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop, causing the app to process attacker-supplied data under the victim tenant's identity.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that string is only the raw body: [1](#0-0) [2](#0-1) 

The `shop` accessor is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not included in `to_signable_string` at all.

`HmacValidator.validate_signature` computes the HMAC with `Context.api_secret_key` — a single secret shared across every shop that installed the app, not scoped per tenant: [3](#0-2) 

`Registry.process` validates only that HMAC and then immediately trusts `request.shop` to build the metadata delivered to the app's business logic: [4](#0-3) 

Since the identity binding broken here is: `shop authenticated by HMAC` ≠ `shop used by the handler (request.shop from header)`, any party who can obtain one valid `(raw_body, hmac)` pair — trivially available to any attacker who installs the app on their own store and triggers a webhook for it (a normal, unprivileged action) — can replay that exact body/HMAC pair to the app's public webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` because it never checks the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook handler relies on: handlers built on this gem's abstraction (`WebhookMetadata#shop`) will process attacker-controlled webhook bodies as if they came from an arbitrary victim shop. Depending on how the host application uses `data.shop` (e.g., to look up/mutate per-shop records, to key writes, to trigger shop-specific side effects), this enables cross-tenant data injection/corruption — a Critical-tier cross-tenant access impact, since the confusion is rooted entirely in this gem's `Webhooks::Request`/`Registry` code, not host misuse of an undocumented API.

### Likelihood Explanation
Moderate-to-high: it requires the attacker to be able to install the target app on a shop they control (a normal, unprivileged step available to anyone) in order to obtain one valid `(body, hmac)` pair, and requires the webhook endpoint to be reachable directly over HTTP (standard for Shopify app webhook endpoints). No access to `api_secret_key`, access tokens, or the victim's credentials is needed — only replay of a legitimately obtained signature with a swapped header.

### Recommendation
Bind the asserted shop (and other identity-relevant headers such as topic/webhook-id) into the HMAC-signable content, or otherwise cryptographically tie the `shop-domain` header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and encourage per-shop webhook validation, or embed a shop-scoped signature component instead of relying purely on the shared `api_secret_key` over the body.

### Proof of Concept
1. Attacker creates/owns Shop A and installs the target app; triggers a webhook (e.g., `products/update`) whose body they fully control (create a product with attacker-chosen fields).
2. App's webhook endpoint (built with `ShopifyAPI::Webhooks::Registry.process`) receives the legitimate request from Shopify with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: H`, raw body `B`. Because HTTP request/response can be observed by the attacker via their own reverse-proxy/logging in front of their own webhook receiver endpoint (which they control, since it's their app installation and they can point the delivery URL to infrastructure they observe before forwarding to the real app, or simply run their own instance of the app under test to learn valid `(B,H)` pairs offline), the attacker records `(B, H)`.
3. Attacker sends a forged POST directly to the production app's public webhook URL with the exact same raw body `B`, header `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `B` and `H` against `Context.api_secret_key`. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and invokes the app's handler, which now acts on attacker-controlled data believing it originated from `victim-shop.myshopify.com`.

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
