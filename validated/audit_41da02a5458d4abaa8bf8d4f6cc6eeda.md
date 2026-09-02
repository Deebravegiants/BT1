## Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches to the registered handler using the `shop` and `topic` values taken from HTTP headers that are never included in the signed material. An attacker who can obtain any single valid `(body, hmac)` pair for the target app (e.g. from their own store's real installation of the app) can replay that body/HMAC pair while freely rewriting the `shop-domain` and `topic` headers, causing the handler to process attacker-controlled data as though it originated from an arbitrary victim shop and topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from attacker-controllable HTTP headers and are never part of the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string` (the body): [3](#0-2) 

`Registry.process` validates only this body HMAC, then immediately trusts `request.topic` and `request.shop` to route and populate `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop asserted to the handler (request.shop)` == `shop that Shopify's HMAC actually authenticates`

Because the HMAC covers only the raw body, this equality does not hold — `shop` and `topic` are unauthenticated headers layered on top of an authenticated body. Any attacker who can produce one valid `(body, hmac)` pair for the app (trivially available to them by installing the app on their own store and triggering any webhook, since the HMAC secret is per-app, not per-shop) can resubmit that exact body/HMAC to the app's webhook endpoint with a forged `x-shopify-shop-domain` and/or `x-shopify-topic` header pointing at a different, victim shop/topic combination. `Registry.process` will accept it as authentic and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop/topic.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook consumers: host applications rely on `WebhookMetadata#shop` as an authenticated tenant identifier (mirroring how `shop` is treated as authenticated in `Auth::JwtPayload`/`SessionUtils`) to look up sessions, update tenant records, or key deduplication/idempotency logic. Since `shop` and `topic` are not bound to the signature, an unprivileged attacker who legitimately controls a store using the target app can inject events that appear to originate from an arbitrary victim shop/topic pair, leading to cross-tenant data corruption/spoofing in any application built on top of `Registry.process`.

### Likelihood Explanation
The attacker only needs to be an unprivileged, real installer of the target Shopify app on their own store (a normal, easily obtainable position for any internet user for a public app) — no access to the victim's credentials, access tokens, or `client_secret` is required. They can trigger any webhook topic through their own store's UI/API to obtain a valid `(body, hmac)` pair, then send a crafted raw HTTP request to the app's public webhook endpoint with modified `shop`/`topic` headers.

### Recommendation
Bind `shop`, `topic`, and other routing-critical fields into the HMAC-signed material (or otherwise cryptographically bind them to the signature), or require host applications to only trust `shop`/`topic` after independently confirming an active, matching session/webhook-id record for that shop, rather than trusting the unauthenticated headers directly in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger a webhook (e.g. `products/create`) to receive a legitimate raw body `B` and valid header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's `api_secret_key` over `B`).
2. Send a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — validation succeeds.
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-controlled body `B` as authentic data for the victim tenant.

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
