### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `topic`, `shop`, `api_version`, and `webhook_id` fields entirely from unauthenticated HTTP headers, while `Utils::HmacValidator` (invoked in `Registry.process`) only verifies the raw request body against the app's single, shop-agnostic `api_secret_key`. The `shop` value handed to the app's `WebhookHandler` is never bound to the HMAC-verified content, breaking the identity equality that should hold: `shop_authenticated_by_signature == shop_used_by_handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the webhook by calling `Utils::HmacValidator.validate(request)`, which computes the signature only over `to_signable_string` (i.e., the body) and compares it with `OpenSSL.secure_compare`: [3](#0-2) [4](#0-3) 

After a successful HMAC check, `request.shop` (the unauthenticated header value) is passed directly into `WebhookMetadata`, which the host application's `WebhookHandler#handle` uses to attribute the event to a tenant/shop: [5](#0-4) [6](#0-5) 

Crucially, `Context.api_secret_key` is a single secret shared by the app across **all** shops that install it — it is not per-shop: [7](#0-6) 

This means any unprivileged party who legitimately controls a Shopify store that has installed the target app can obtain a validly-signed webhook (body + HMAC) for their own shop from a real Shopify webhook delivery. Because the HMAC only signs the body — never the `X-Shopify-Shop-Domain` header — that attacker can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still return `true` (the body is untouched and the secret is shared across tenants), yet `Registry.process` will construct `WebhookMetadata` with `shop: <victim_domain>`, causing the host application to execute business logic (e.g., updating billing records, provisioning, revoking access, order/fulfillment side effects) attributed to a shop the attacker does not control.

This directly parallels the referenced report's bug class: a value used for a security-relevant decision (`request.shop`) is disjoint from the value actually covered by the cryptographic check (`raw_body` only), breaking `shop_authenticated == shop_acted_on`.

### Impact Explanation
This is a cross-tenant identity binding break: an attacker who is a legitimate customer of the app (installed on their own store) can forge webhook events that are processed by the app as if they originated from a different merchant's shop, despite a "passing" HMAC check. Depending on what the host app does inside `WebhookHandler#handle` (which nearly always trusts `data.shop` as the tenant key, per the gem's documented usage pattern), this enables cross-tenant data manipulation/injection — e.g., forcing `app/uninstalled`, `shop/redact`, or business-topic webhooks to be applied against a victim shop's tenant record without ever having credentials for that shop. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that has published/documented webhook topics and is installed by more than one merchant (a completely unprivileged prerequisite — anyone can install a public Shopify app on a dev/test store). No access token, `client_secret`, or privileged account is required; the attacker only needs to be a normal merchant of the same app, capture one legitimate webhook delivery to their own store, and replay it with a modified header to the app's public webhook endpoint.

### Recommendation
Bind the tenant identity into the HMAC-verified material, or otherwise cryptographically tie `shop` to the signed payload before it is trusted:
1. Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the signable string that `HmacValidator` verifies, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signed params.
2. Alternatively, cross-check `request.shop` against an independently verified source (e.g., a per-shop registered webhook record / access token lookup) before invoking the handler, rather than trusting the header outright.
3. Document/enforce that `WebhookHandler` implementations must not treat `data.shop` as authenticated unless the gem itself binds it to the signature.

### Proof of Concept
1. Attacker installs app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw HTTP request Shopify sends, including a valid `X-Shopify-Hmac-Sha256` header computed with the app's shared `api_secret_key`.
2. Attacker replays the identical request to the app's webhook endpoint but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (leaving body and HMAC header untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the shared secret: [8](#0-7) 
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"` and passed to the app's handler, which processes the event as belonging to the victim tenant — despite the attacker never having any credential for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
