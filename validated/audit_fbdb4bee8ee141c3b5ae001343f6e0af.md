## Title
Webhook Tenant Impersonation via Unauthenticated `shop-domain`/`topic` Headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed only over the raw request body, but it dispatches the webhook to application handlers using `shop`, `topic`, and `webhook_id` values that are read from HTTP headers which are never included in that HMAC computation. This breaks the binding between "the body whose authenticity was proven" and "the shop identity the app trusts as the source," allowing a party who legitimately receives one authentic `(raw_body, hmac)` pair for their own shop to relabel it as coming from any other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from request headers, none of which factor into `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body check, then immediately trusts `request.topic` and `request.shop` (both header-derived, unauthenticated) to select the handler and build the metadata passed into application code: [3](#0-2) 

The identity binding that should hold is:

`shop_bound_to_authenticated_bytes (the tenant whose secret validly signed raw_body) == shop_used_for_dispatch (request.shop header trusted by Registry.process)`

Because the HMAC only covers `raw_body` and never the `shop-domain` header, this equality is not enforced by the gem. Any party who can obtain one authentic `(raw_body, hmac)` pair — for example, an unprivileged user who installs the app on their own trial/free shop and receives a legitimate webhook — can replay that exact body and HMAC to the app's webhook endpoint while swapping the `shopify-shop-domain` (or `x-shopify-shop-domain`) header to name a different, victim shop. `Utils::HmacValidator.validate` recomputes the signature over `to_signable_string` (the unchanged raw body) and it still matches, so `Registry.process` accepts the request and calls the handler with `WebhookMetadata` claiming the victim shop's identity.

### Impact Explanation
This is a cross-tenant identity confusion: application code that keys business logic (session lookups, order processing, data mutation, uninstall/GDPR handling, etc.) off `WebhookMetadata#shop` will act on the wrong tenant's data/session because the gem itself provides no way to bind the verified bytes to the claimed shop. This maps to "cross-tenant access," a Critical-impact category, since the app is fully within its rights to trust `data.shop` — the interface promises an authenticated webhook payload.

### Likelihood Explanation
An attacker only needs the ability to receive one authentic webhook for a shop they control (trivial — any Shopify Partner/store owner installing the same public app can do this) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint (no credentials, no TLS interception, no `api_secret_key` required). This satisfies the "unprivileged internet user" bar in scope.

### Recommendation
Extend `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` to also bind the security-relevant headers (`shop`, `topic`, `webhook_id`) into the signed material, or otherwise cryptographically bind the header-derived shop to the payload before dispatch (e.g., cross-check against the request's TLS/host context, or require the consuming app to independently corroborate `shop` against a known/installed-shop list before trusting `WebhookMetadata#shop`). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are NOT covered by the HMAC and must not be treated as authenticated by `Registry.process` alone.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `x-shopify-hmac-sha256` header value `H` sent by Shopify (both authentic, since Shopify itself signed `B` with the app's shared secret).
2. Attacker sends a new HTTP request to the same app's webhook endpoint with body `B` unchanged, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com` and any `x-shopify-topic` of choice.
3. `Utils::HmacValidator.validate(request)` recomputes HMAC over `request.to_signable_string` (`= B`) and it matches `H`, so validation succeeds: [4](#0-3) 
4. `Registry.process` looks up the handler by `request.topic` (attacker-controlled) and invokes it with `shop: request.shop` set to `victim-shop.myshopify.com`, even though the shop never sent or authorized this webhook: [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
