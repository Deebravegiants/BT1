### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then reads the tenant identity (`shop`) from a separate, unauthenticated HTTP header. Because the `shop-domain` header is never part of the signed material, any request bearing a *valid* HMAC for a given body can carry an arbitrary `shop` value, breaking the binding between "body verified by HMAC" and "shop attributed to that body."

### Finding Description
`Webhooks::Registry.process` validates a webhook exclusively via: [1](#0-0) 

The HMAC check is performed by `Utils::HmacValidator.validate`, which computes the signature purely over `to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — it never incorporates the `shop`, `topic`, or `webhook-id` headers: [3](#0-2) 

The `shop` value handed to the app's handler is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the HMAC-covered body: [4](#0-3) 

The documented contract explicitly promises that `process` "will verify the request did indeed come from Shopify" and that `data.shop` is trustworthy: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac_valid(body, api_secret_key) ⇒ shop == the shop that actually produced body`. In this implementation, that equality does not hold, because `shop` is sourced from an unsigned header while the HMAC only binds `(api_secret_key, body)`.

Since `api_secret_key` is the app's single client secret shared across every shop that has installed the app, any shop that has installed the app can trigger a legitimate webhook to itself (e.g. `orders/create`), capture the resulting `(raw_body, hmac)` pair that Shopify delivers to it, and replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with any other shop's domain. `HmacValidator.validate` will still succeed, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, while `body` still contains attacker-controlled content originating from the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged app installer (any merchant able to install a public app) can forge webhook events that host applications will process as belonging to a different, victim shop, using only a legitimate webhook of their own shop as raw material. Any app whose webhook handler uses `data.shop` to select which tenant's database record to update, create, or delete (a common and reasonable pattern this gem's own docs recommend: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) is exposed to cross-tenant data injection/corruption without needing the victim's access token, `client_secret`, or any credential belonging to the victim.

### Likelihood Explanation
Exploitation requires only that the attacker be an installer of the target app on their own store (or otherwise able to trigger a webhook addressed to them) and be able to send an arbitrary HTTP POST to the app's public webhook endpoint with modified headers — both trivially available to an "unprivileged internet user." No secrets beyond ordinary app installation are needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is actually authenticated, e.g. by validating that the `shop-domain` header corresponds to a shop with a currently known/registered installation (session) before trusting it, or by requiring the host application to independently verify `shop` against its own installed-shops list before acting on webhook data — and document this requirement clearly, since currently the docs imply `process`/`data.shop` are already fully verified.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers for `orders/create`.
2. Attacker places an order, causing Shopify to POST a webhook to the app's callback URL with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`), plus `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` and re-sends a POST to the same webhook endpoint, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B`.
5. The handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"` and `body` containing attacker-controlled content from step 2, even though `victim.myshopify.com` never generated this event.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
