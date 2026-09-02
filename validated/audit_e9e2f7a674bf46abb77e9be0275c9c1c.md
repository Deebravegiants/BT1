### Title
Webhook `shop-domain` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing — (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop-domain` header — the value the gem treats as the tenant identity for the event — is never included in the signed material. Since the webhook HMAC secret (`Context.api_secret_key`) is a single, app-wide secret shared across every installed shop (not per-tenant), anyone who can obtain one valid `(body, hmac)` pair for the app — e.g. by installing the app on their own store and capturing a genuine webhook Shopify sends them — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` accepts this because it only re-verifies the HMAC over the body, then hands the attacker-controlled `shop` straight to the app's handler.

### Finding Description
The binding that should hold is:
`hmac == HMAC(secret, body)` **and** `shop used by the handler == shop that produced the body`.

In practice only the first half is enforced:

- `Request#to_signable_string` signs `@raw_body` alone: [1](#0-0) 
- `Request#shop` is read straight from the (attacker-supplied, unauthenticated) header, independent of the signed content: [2](#0-1) 
- `HmacValidator.validate` / `validate_signature` compute the digest solely over `to_signable_string`, i.e. the body, with the app's single shared `api_secret_key`: [3](#0-2) 
- `Registry.process` verifies only that HMAC, then forwards `request.shop` unchecked to the registered handler as the webhook's tenant identity: [4](#0-3) 

Because the same `api_secret_key` authenticates webhooks for *every* shop that has installed the app, a valid `(body, hmac)` pair obtained from one tenant (including a tenant the attacker legitimately controls, such as their own free/dev store) is valid for *any* shop-domain header. The gem never checks that the `shop-domain` header is consistent with the shop the body actually originated from — that check simply doesn't exist in the signed material or in `Registry.process`.

This is the same identity-binding class as the referenced report: a value acted upon (`baseTokenId`/here, the tenant `shop`) is not the value actually covered by the authenticity check (`_tokenId`/here, the raw body only).

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately installs the app on their own shop (no special privilege, no leaked secret) can forge webhook events that the host application will attribute to a victim shop. Any host logic keyed off `WebhookMetadata#shop` (e.g., app-uninstalled handling, order/customer data ingestion, GDPR webhooks, billing state changes) can be triggered for an arbitrary victim shop domain the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on any shop the attacker controls (routine, unprivileged, self-service on Shopify), and (2) the ability to send an HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header (or `x-shopify-shop-domain`) while keeping body and HMAC unchanged. No access token, `api_secret_key`, or victim credentials are needed.

### Recommendation
Bind the shop identity into the authenticity check, e.g. include the shop domain (and/or webhook id/topic) in the signed material used by `HmacValidator`, or — at minimum — have `Registry.process`/the host app cross-check `request.shop` against the shop that owns the currently active session/subscription for that webhook id before invoking the handler, rejecting requests where the claimed shop cannot be reconciled with the signed payload.

### Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker.myshopify.com"
# and captures one genuine webhook Shopify sends them:
raw_body = '{"id":123,"note":"legit order from attacker shop"}'
hmac_b64 = "<value Shopify actually sent in x-shopify-hmac-sha256>"

# Attacker now replays the identical body/hmac to the app's public
# webhook endpoint, but swaps the shop-domain header to the victim:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,          # unchanged, still verifies
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (Utils::HmacValidator.validate uses only raw_body),
#    handler.handle is invoked with data.shop == "victim-shop.myshopify.com"
```

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
