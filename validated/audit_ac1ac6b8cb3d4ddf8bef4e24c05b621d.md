## Title
Webhook HMAC Validation Does Not Cover the `shop-domain`, `topic`, or `webhook-id` Headers, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once `Utils::HmacValidator.validate(request)` succeeds, then dispatches the handler using `request.shop`, `request.topic`, and `request.webhook_id`. However, `Request#to_signable_string` signs only the raw body, so none of those identity-bearing headers are covered by the HMAC.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are read straight from HTTP headers, entirely outside the signed content: [3](#0-2) 

`Registry.process` gates on the HMAC check and then trusts `request.shop`/`request.topic` for dispatch and tenant attribution: [4](#0-3) 

The identity binding broken is:
`HMAC-verified(body)` ≠ `shop used for tenant routing`

Since the same `api_secret_key` (the app's single `client_secret`) is used to validate webhooks for every shop that installed the app, any merchant who legitimately installs the app can capture one authentic webhook delivery (valid body + valid `hmac` header) from their own store. Because the `shop-domain` (and `topic`/`webhook-id`) headers are not part of the signed material, that same body+hmac pair can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` (it never looks at the shop header), and `Registry.process` will hand the attacker-chosen `shop` value to the app's `WebhookHandler`, which typically uses it to look up/mutate that shop's records.

### Impact Explanation
This is a cross-tenant confusion vector: an unprivileged install (any merchant able to install the app in their own store) can cause the app's webhook processing pipeline to attribute attacker-controlled payload data to a different, victim shop, since the only integrity check (HMAC) never binds the shop identity. Depending on how the host app's `WebhookHandler` uses `shop` (e.g., to select which tenant record to update/delete, e.g. for `app/uninstalled`, `shop/redact`, `customers/data_request` handlers), this can lead to unauthorized cross-tenant data manipulation or disclosure — classified Critical (cross-tenant access) per the scope's impact list.

### Likelihood Explanation
Requires only: (1) the attacker be able to install the target app on their own shop (or otherwise trigger one webhook delivery to themselves) to obtain a validly-HMAC'd `(body, hmac)` pair, and (2) the ability to POST arbitrary headers to the app's public webhook endpoint — both are available to any unprivileged internet-facing merchant/attacker, with no access token, `client_secret`, or privileged account required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value verified against `hmac`, or otherwise cross-check the `shop` header against a value derivable from an authenticated source (e.g., verify the shop is one to which the currently active session's access token belongs before dispatching), rather than trusting `request.shop` solely because the raw body's HMAC checked out.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook (e.g., `orders/create`) to the app's endpoint with a valid `x-shopify-hmac-sha256` header for that raw body.
2. Attacker captures the raw `body` and `hmac` header value from that delivery (e.g., via a local proxy/webhook debug tool they control).
3. Attacker replays the exact same `body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes (it only checks the body), then invokes the handler with `shop: "victim-shop.myshopify.com"` — the app's handler now processes attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
