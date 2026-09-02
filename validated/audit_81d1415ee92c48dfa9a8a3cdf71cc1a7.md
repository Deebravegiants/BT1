## Finding [1](#0-0) [2](#0-1) 

### Title
Webhook shop-domain identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for whatever shop is named in the `X-Shopify-Shop-Domain` header once the HMAC check passes, but the HMAC is computed and verified over the raw request body only — the shop domain is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (`OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string`) authenticates nothing but the JSON payload bytes: [2](#0-1) [3](#0-2) 

`Registry.process` then trusts `request.shop`, which is read straight from the `shopify-shop-domain` header and is not covered by the signature, and forwards it to the caller's handler as the tenant identifier: [4](#0-3) [1](#0-0) 

The equality the gem should enforce is: `shop authenticated by HMAC == shop delivered to the handler`. In reality, only `body authenticated by HMAC == body delivered to the handler` holds; `shop` is asserted, not verified. Because the `api_secret_key` used to compute the HMAC is a single app-wide secret shared across every shop that has installed the app (not per-shop), any unprivileged merchant who has installed the app can capture a genuinely Shopify-signed webhook delivered to their own store (valid body + valid HMAC), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

This directly matches the documented promise in the gem's own usage guide, which states that `Registry.process` "will verify the request did indeed come from Shopify" — implying the whole request, including the shop attribution, is authenticated: [5](#0-4) 

That guarantee is broken for the `shop` field specifically.

### Impact Explanation
A merchant who has installed the app (an unprivileged, non-Shopify-employee internet user relative to other tenants) can forge webhook deliveries that are misattributed to any other shop domain, since the shop field carries no cryptographic binding. Depending on how the host handler uses `data.shop` (e.g., to key GDPR `customers/redact`/`shop/redact` processing, update per-shop state, or drive shop-scoped side effects), this enables cross-tenant data confusion/corruption — one tenant forcing the app to believe an event happened for another tenant. This satisfies the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Exploitation only requires: (1) being a legitimate app installer able to receive at least one real webhook (trivial — install the app, trigger any subscribed event), and (2) the ability to replay an HTTP POST with a modified header, both of which are within reach of any ordinary merchant/customer of the app and require no `api_secret_key`, no stolen access token, and no privileged access.

### Recommendation
Bind the shop identity into the signed material the library trusts, e.g., by requiring the handler/registry to cross-check `request.shop` against the shop associated with the specific `webhook_id`/subscription registered via the Admin API, or by rejecting webhooks whose `shop` was not the one the corresponding registration was created for. At minimum, document prominently (and enforce in `Registry.process`) that `request.shop` is unauthenticated and must never be used as a trust boundary without an independent server-side shop lookup.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) and capture the resulting POST — raw body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's shared `api_secret_key`).
2. Replay the exact same body `B` and HMAC `H` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (it only checks `B` against `H`), and `Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the event was never delivered by Shopify for that shop.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
