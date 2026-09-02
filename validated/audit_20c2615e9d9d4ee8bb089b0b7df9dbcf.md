### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` only validates the HMAC over the webhook's raw body, but the `shop` identity that the library hands to the app's handler is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed material. This breaks the intended binding `shop authenticated == shop acted upon`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively from `verifiable_query.to_signable_string`, and for webhook requests that method returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` header without any cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` verifies only the HMAC of the body and then forwards the unauthenticated `shop` header value straight into `WebhookMetadata`, which is passed to the app's handler as the trusted tenant identity for the event: [3](#0-2) 

Because the HMAC is computed with the app's single shared `api_secret_key` (the same secret is used for every shop that installs the app) and is only bound to the body bytes, `(hmac, raw_body)` pairs are valid regardless of which `shop` header accompanies them. This is precisely the "field acted on but not covered by the HMAC" class of bug: the equality that should hold is `shop bound in HMAC == shop delivered to handler`, but the actual state is `shop bound in HMAC == undefined` while `shop delivered to handler == unauthenticated header value`.

### Impact Explanation
An unprivileged internet user who controls their own shop installation of the target app can capture a legitimate `(raw_body, hmac)` pair generated for their own tenant (e.g. by triggering `orders/create`, `app/uninstalled`, `customers/data_request`, etc. on their own store) and then replay that exact body/HMAC to the app's public webhook endpoint while substituting a different `shopify-shop-domain` header value naming a victim shop. `Utils::HmacValidator.validate` will still pass because it only checks the body against the shared secret, and `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop. Any app logic that keys off `data.shop` to look up sessions, update per-shop state, or fulfil compliance webhooks (`customers/redact`, `shop/redact`, `customers/data_request`) would act on the wrong tenant, which is a cross-tenant integrity violation reachable purely by an internet-facing HTTP request to the app's public webhook route.

### Likelihood Explanation
Requires only: (1) being able to install the app on an attacker-controlled shop to legitimately obtain one valid `(body, hmac)` pair for a chosen topic, and (2) sending a crafted HTTP POST to the app's webhook endpoint with that body/HMAC and a forged `shopify-shop-domain` header. No secret, token, or privileged access is needed - both prerequisites are available to any unprivileged internet user who can install a free/dev app instance.

### Recommendation
Do not treat the `shopify-shop-domain` (or `x-shopify-shop-domain`) header as trusted tenant identity based solely on validating the HMAC of the body. Either include the shop domain (and topic/webhook-id) in the signed material used by `HmacValidator`, or require the host application to cross-check the header `shop` against a shop that is independently known to be installed/authorized before acting on the event, and document this requirement clearly in `Webhooks::Registry`/`WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real webhook (e.g. `customers/data_request`) delivered with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-for-body>`, and some `raw_body`.
2. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from that delivery (e.g. via their own server logs, since it was sent to their own webhook endpoint).
3. Attacker POSTs the same `raw_body` and `x-shopify-hmac-sha256` to the same app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only and it matches, since the header is not part of the signable string (`lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the app handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the request body actually pertains to the attacker's own shop event.

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
