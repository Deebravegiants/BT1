### Title
Webhook HMAC Validation Does Not Cover the `shop-domain` or `topic` Headers, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature that `Utils::HmacValidator.validate` checks in `Webhooks::Registry.process` never covers the `shop-domain` or `topic` headers that the same method later trusts to identify the tenant and dispatch the handler.

### Finding Description
`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`: [1](#0-0) 

That method returns `@raw_body` only — the `hmac`, `topic`, and `shop` accessors are all derived from separate HTTP headers that are never part of the signed string: [2](#0-1) 

`Registry.process` then uses `request.topic` to select the handler and forwards `request.shop` straight into the `WebhookMetadata` object the app's handler acts on, based solely on the fact that `Utils::HmacValidator.validate` returned true: [3](#0-2) 

The equality the code implicitly assumes but never enforces is:
`shop header value == shop that produced the HMAC-signed body`

Because the HMAC only binds the body, any request whose body byte-for-byte matches a previously (or independently) HMAC-valid body will pass validation regardless of the `shop-domain`/`topic` headers attached to it. A merchant who has the app installed on their own store receives genuinely-signed webhook deliveries (body + valid HMAC) for their own shop. Since the headers are not signed, they can resend the exact same body/HMAC pair to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain (and/or `X-Shopify-Topic` changed to a different registered topic whose handler doesn't care about body shape, e.g. `app/uninstalled`, `shop/redact`, or any topic with a body they can naturally get e.g. `{}`). `Utils::HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` calls the victim topic's handler with `shop: "victim-shop.myshopify.com"`.

### Impact Explanation
This crosses a tenant boundary: an unprivileged merchant (who legitimately installed the app on their own store and thus receives real, signed webhook deliveries) can make the app process webhook data under an arbitrary other shop's identity, without possessing that shop's credentials, access token, or the app's `client_secret`. Depending on the handler's logic (e.g., deprovisioning on `app/uninstalled`, GDPR data deletion on `shop/redact`/`customers/redact`, or state updates keyed by `shop`), this can trigger cross-tenant data corruption, wrongful data deletion, or state changes attributed to a shop that never sent the request — matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Any merchant with the app installed can obtain a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair simply by using the app normally (e.g., triggering `app/uninstalled` themselves, or waiting for a mandatory webhook with a fixed/predictable minimal body). Replaying that exact body with modified `shop-domain`/`topic` headers to the app's public webhook endpoint requires no secret material and no special access — only the ability to send an HTTP request, which is available to any internet user who controls a shop where the app is installed.

### Recommendation
Do not trust `shop`/`topic` header values based solely on body-HMAC validity. Either:
- Include the `shop-domain` and `topic` header values in the signed material used for validation (not possible without changing Shopify's platform-level signing, so instead:)
- Cross-check `request.shop` against the shop associated with the registered webhook subscription (e.g., verify the shop is a currently-installed shop known to the app, and correlate the delivery with the specific tenant it was registered for) before dispatching to a handler, and treat `shop-domain`/`topic` headers as untrusted input for authorization decisions, requiring the application to independently confirm tenant identity (e.g., via a stored mapping of `webhook_id` to expected shop) rather than trusting the header verbatim.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers/receives a webhook for a topic with a fixed/minimal body (e.g. `app/uninstalled`, body `{}`), capturing the raw POST: headers including `X-Shopify-Hmac-Sha256: <valid-hmac-for-"{}">`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: app/uninstalled`, body `{}`.
2. Attacker resends the identical body `{}` and identical `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (`@raw_body == "{}"`), which matches the attacker-supplied `hmac`, so validation succeeds.
4. `Registry.process` looks up the handler for `topic` and invokes it with `shop: "victim-shop.myshopify.com"` [4](#0-3) , causing the app to execute the `app/uninstalled` (or other) handler logic as if it were `victim-shop.myshopify.com`, despite the attacker never having any credential for that shop.

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
