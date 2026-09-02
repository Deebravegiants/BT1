### Title
Webhook `shop` (and `topic`) identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (and `topic`) values that are handed to the application's webhook handler are read directly from unauthenticated HTTP headers that are never included in the signed bytes. This breaks the intended binding `HMAC-verified-bytes == identity-used-by-handler`, allowing a party who already has one legitimately-signed webhook body from the same app (e.g. because they installed the app on their own store) to replay that body while spoofing the `shop-domain` header to point at a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic linkage to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only compares the HMAC of `to_signable_string` (i.e. the raw body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` trusts this validation result and then forwards `request.shop` (an unverified header) straight into the handler's metadata, which host applications use to attribute the event to a specific merchant/tenant: [4](#0-3) 

The identity equality that should hold is: `shop-that-generated-the-signed-bytes == shop-value-the-handler-acts-on`. Because `shop` is not part of `to_signable_string`, this equality is never enforced — the HMAC only proves "this body was signed with the app's `api_secret_key`" and says nothing about which shop it belongs to. Since a single app uses one shared `api_secret_key` across every shop that installs it, any party who can obtain one valid `(raw_body, hmac)` pair (trivially, by installing the app themselves and capturing a webhook Shopify sends them) can resend that exact body/HMAC pair to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass because the body/HMAC combination is genuinely valid, and `Registry.process` will dispatch to the handler claiming the payload came from the victim shop.

### Impact Explanation
This is a cross-tenant access issue: an attacker (an unprivileged internet user who merely installs the target app on their own store, a legitimate, unprivileged action) can make the host application process attacker-chosen webhook content while it believes the event originated from a different, victim merchant. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up which merchant's order/customer/inventory record to update, or to fetch that shop's stored access token/session for follow-up API calls), this can lead to data corruption, unauthorized actions taken against another tenant's store, or information disclosure across tenants — squarely matching the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Likelihood is realistic but not trivial: the attacker must be able to install the target app on a shop they control (a normal, permitted, unprivileged action for any Shopify Partner/developer/merchant) in order to obtain one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`. No possession of the `api_secret_key` itself, access tokens, or any privileged credential is required — only network access to the app's public webhook endpoint and the ability to replay an HTTP request with modified headers.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material, or otherwise cryptographically tie them to the verified body:
- Include the `shop-domain` (and `topic`) header values in `to_signable_string` so they are covered by the HMAC, matching how Shopify's platform actually computes the digest server-side if it includes routing metadata, or
- Require host applications to independently verify that `request.shop` corresponds to a shop for which this specific webhook was actually registered (e.g., cross-check against a per-shop webhook secret or a stored expected topic/shop pairing) before trusting `WebhookMetadata#shop`, and document this requirement prominently since the gem currently implies the header is trustworthy once `HmacValidator.validate` passes.

### Proof of Concept
1. Attacker registers the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Shopify sends the attacker a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` and sends a forged HTTP request directly to the app's public webhook endpoint:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (spoofed)
   - Body: `B` (unchanged)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it equals `H` — validation passes. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)`, causing the host app to process attacker-controlled data attributed to the victim shop. [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
