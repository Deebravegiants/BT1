### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook using `Utils::HmacValidator.validate(request)`, but the HMAC is computed only over the raw request body. The `shop-domain` header, which the library subsequently trusts as the tenant identity passed to the webhook handler, is never included in the signed bytes. An attacker who can obtain one legitimately-signed webhook body/HMAC pair (e.g. from their own shop, where the app is installed) can replay it with an arbitrary `X-Shopify-Shop-Domain` header and have it processed as if it belonged to a different shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers the body) and then immediately hands `request.shop` — the unauthenticated header — to the app's webhook handler as the tenant identifier, alongside the (now-implicitly-trusted) parsed body: [3](#0-2) 

The identity binding broken here is: `hmac-sha256(raw_body, client_secret)` is treated as proof of `(shop, topic, raw_body)` authenticity, when it is only proof of `raw_body` authenticity — `shop` (and `topic`, `api_version`, `webhook_id`) are attacker-controllable HTTP headers with no cryptographic tie to the signature. This is the same "field acted on but not covered by the HMAC" pattern as the mismatched-parameter DoS in the source report, except here it breaks a tenant/identity boundary instead of merely causing a revert.

### Impact Explanation
Because the client_secret (HMAC key) is shared across all shops that install a given app, any shop that has the app installed can legitimately obtain a validly-signed `(raw_body, hmac)` pair from its own webhook deliveries. That attacker-controlled shop can then resend the same body/HMAC to the app's webhook endpoint while forging the `shop-domain` header to name a victim shop. `Registry.process` will pass the HMAC check (only the body is checked) and route the data to the handler tagged with the victim's shop domain. If the host application uses `WebhookMetadata#shop` to look up or mutate per-tenant state (order/customer data, redaction flags, uninstall handling, etc.), this results in cross-tenant data corruption/impersonation — writing or acting on data under a shop identity the attacker does not control. This satisfies the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker who is a merchant/user of the app on at least one shop: they need no secrets beyond what Shopify already sends them for their own webhooks, and no privileged credentials are required — only observing their own legitimate webhook traffic and replaying it with a modified header to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic) identity into what is verified before it's trusted:
- Include the shop domain (and topic) in the signed/verified material, or independently verify that the shop in the header matches a shop known to have installed the app and is expected to receive that topic, before trusting `request.shop`.
- At minimum, cross-check `request.shop` against the shop associated with the session/access token used to register that specific webhook subscription, rather than trusting the header outright once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g. `orders/create`), capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header — both valid per `HmacValidator.validate`.
2. Attacker POSTs the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `request.to_signable_string` (`raw_body`) — validation succeeds.
4. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host application to process attacker-supplied data under the victim shop's identity.

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
