### Title
Webhook shop-tenant spoofing via unsigned HTTP headers — HMAC only covers the body, not the shop identity ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), event `topic`, and `webhook_id` from HTTP headers, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. Any party who can obtain one valid, HMAC-signed webhook delivery (e.g. by installing the app on their own store and triggering a webhook) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers to impersonate any other shop. `Registry.process` accepts the request as authentic and hands the attacker-chosen `shop` value straight to the app's webhook handler, which is the standard signal apps use to route/persist per-tenant data (see `docs/usage/webhooks.md`, `data.shop`).

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers, outside the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e. the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation as the sole authenticity check, then dispatches the handler using the *header-derived* (unverified) `shop`: [4](#0-3) 

The broken identity binding is:
```
shop_bound_in_hmac_signed_payload  !=  shop_used_to_route/identify_the_tenant (request.shop, from header)
```
Since the header is not part of the signable string, these two values can diverge without invalidating the signature. Any legitimate, unprivileged holder of one valid webhook (their own store's install) can forge a delivery that is accepted as coming from a different shop.

### Impact Explanation
This is a cross-tenant identity confusion: the app-level webhook handler (per the gem's documented usage, `docs/usage/webhooks.md` lines 10-29) receives `data.shop` and typically uses it as the tenant key to persist or act on data (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)`). An attacker-controlled `shop` value that passes HMAC validation lets a malicious merchant inject events attributed to a victim shop into the host application's per-tenant processing pipeline — a cross-tenant access primitive, without needing the app's `client_secret`.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the app on a store they control (a normal, unprivileged action) and capture one legitimate webhook HTTP request to their own endpoint (visible via any request logging/proxy they control, since it's delivered to *their* server). No secret material or elevated privilege is required — the attacker never needs `api_secret_key`; they only need to replay a body/HMAC pair they already legitimately received, with modified headers, which is trivial with any HTTP client.

### Recommendation
Bind the shop identity to the HMAC-covered content. Bind the `shop-domain` (and ideally `topic`/`webhook-id`) headers into the value that is HMAC-verified — for example by including them in `to_signable_string`, or by independently validating that the header-derived `shop` matches a shop that this app's session store actually has cached credentials for before trusting the webhook payload for routing/persistence. At minimum, document/require that host applications must not trust `data.shop` unless it is cross-checked against known installed shops, and update `Request#to_signable_string` to fail closed instead of trusting an unauthenticated header for tenant identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers for `orders/create` via `ShopifyAPI::Webhooks::Registry.add_registration`.
2. Attacker triggers an order create in their own store; Shopify sends a legitimate webhook to the attacker's registered endpoint with:
   - Body: `{...order json...}`
   - Headers: `X-Shopify-Hmac-Sha256: <valid hmac of body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`
3. Attacker captures this raw request and replays it to the app's webhook controller, but with `X-Shopify-Shop-Domain` changed to `victim-shop.myshopify.com` (body and HMAC header unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates successfully because it only checks `@raw_body` against the (unchanged) HMAC.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)`, causing the host application to process/act as though `victim-shop.myshopify.com` produced this order data.

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
