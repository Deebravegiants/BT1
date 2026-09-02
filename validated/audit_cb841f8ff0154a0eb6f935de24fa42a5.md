### Title
Webhook tenant identity (`shop`) is not bound to the HMAC-verified payload, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers and passed to the app's handler unchanged. `Registry.process` trusts these header-derived values as the tenant identity for dispatching the webhook, without any cryptographic binding between the verified body and the claimed shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is taken straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) to build the `WebhookMetadata` handed to the app-provided handler: [3](#0-2) 

The HMAC secret (`Context.api_secret_key`) is a single **per-app** secret shared across every shop that installs the app — it is not shop-specific. This means:

- Equality that should hold: `shop_bound_to_signed_body == shop_used_by_handler`.
- What actually holds: `hmac_valid(body, app_secret) == true` is fully independent of `shop_header`. The identity binding `shop → signed_payload` does not exist anywhere in `to_signable_string` or `HmacValidator`.

Because the identical app secret is used for all merchants, any actor who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app — trivially available to any merchant who installs the app on their own store and observes/replays a real Shopify webhook delivery to the app's endpoint — can resend that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header values for a different, victim shop. `Utils::HmacValidator.validate` will still return `true` (it only checks the body against the secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop, per the documented `data.shop` contract: [4](#0-3) 

Any host application that follows this documented API and uses `data.shop` to select which tenant's records to update (the officially recommended pattern shown in the docs) will act on the wrong tenant's data using attacker-supplied, unauthenticated body content.

### Impact Explanation
This breaks the tenant/shop identity binding for a Critical-class outcome: cross-tenant access/write. An attacker who is a legitimate (unprivileged) installer of the app on their own store can forge webhook deliveries that the receiving application will process as if they originated from an arbitrary other merchant, injecting attacker-controlled body content (order/product/customer data, GDPR `customers/redact` payloads, etc.) into another tenant's processing pipeline. This satisfies the "cross-tenant access" Critical impact category defined in scope.

### Likelihood Explanation
Moderate-to-high. No secrets, TLS interception, or privileged access are required — only a normal, unprivileged app installation by the attacker on a store they control, followed by capturing one legitimate webhook delivery to the app's public endpoint and replaying it with modified `shop-domain`/`topic` headers. The `HmacValidator` and `Request` code do nothing to prevent this since the shop identity is architecturally outside the signed payload.

### Recommendation
Bind the tenant identity to the verified payload before trusting it:
- Include the `shop-domain` (and `webhook-id`) header values in the signable string used for HMAC verification (or otherwise cryptographically bind them to the signed body), so a replay with a substituted shop fails validation.
- Alternatively/additionally, require callers to supply the expected `shop` for the session under which the webhook is being processed and assert it matches `request.shop` before invoking the handler.
- Document prominently that `data.shop`/`data.topic` are not currently covered by the HMAC and must not be trusted for tenant selection until this is fixed.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action) and triggers an event (e.g., updates a product) to receive a legitimately Shopify-signed webhook at the app's registered HTTP endpoint.
2. Attacker captures the raw body `B` and the valid `X-Shopify-Hmac-Sha256: H` header for this delivery (computed by Shopify using the app's shared `client_secret`).
3. Attacker resends the exact same `B` and `H` to the app's webhook endpoint, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - (optionally) a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against the shared secret — see: [5](#0-4) 
5. `Registry.process` dispatches to the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, and the application (following the documented pattern) processes attacker-controlled body `B` as if it came from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
