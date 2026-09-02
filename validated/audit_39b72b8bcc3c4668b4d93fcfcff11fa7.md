### Title
Webhook HMAC Only Covers the Raw Body, Not the `shop`/`topic`/`webhook-id` Headers, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` passes, then forwards `request.shop`, `request.topic`, and `request.webhook_id` — all values read straight from unauthenticated HTTP headers — into the handler via `WebhookMetadata`. The HMAC signature, however, is computed only over the raw request body, never over these header fields, so the tenant-identifying `shop` value is not bound to the cryptographic proof of authenticity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from HTTP headers with no cryptographic protection: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` computes the HMAC exclusively over `to_signable_string` (i.e., the raw body): [3](#0-2) 

`Registry.process` gates on that same HMAC check and then constructs `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`: [4](#0-3) 

The equality the gem is supposed to enforce is:
`shop authenticated by HMAC == shop attributed to the tenant/session by the handler`

Because the HMAC only proves "this body byte-string was produced with our `client_secret`" and says nothing about which shop, topic, or webhook id that body belongs to, an attacker can take a byte-for-byte legitimately-signed body (obtainable by installing the app on their own shop, since a single app has one shared `client_secret` across every installed shop) and resubmit it with forged `X-Shopify-Shop-Domain` / `X-Shopify-Topic` / `X-Shopify-Webhook-Id` headers claiming to belong to a different (victim) shop. `HmacValidator.validate` still passes because the body is unchanged and genuinely signed, and `Registry.process` hands the forged `shop` value straight to the host application's handler as if it were authenticated.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: any user who can install the app for one shop can forge webhook events (with the real, attacker-controlled body content) and have them attributed to any other `shop` string of their choosing. Any host application that relies on the gem's `WebhookMetadata#shop` (returned only after `HmacValidator` succeeds) to select the tenant/session/data store — a documented and expected usage — will process attacker data under a victim tenant's identity, i.e., cross-tenant data injection/confusion. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any unprivileged internet user: no `api_secret_key`, access token, or privileged account is required — only the ability to install the app on any Shopify development/trial store, which is available to any internet user, in order to harvest one genuinely HMAC-signed body, then replay it against the app's webhook endpoint with modified headers.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the signed material, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, the gem should not present `request.shop`/`request.topic` as verified once `HmacValidator.validate` succeeds, since only the body is actually verified.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and receives a real webhook, e.g. an `orders/create` payload with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's shared `client_secret`.
2. Attacker resends the exact same raw body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com` (and optionally a different `X-Shopify-Webhook-Id`/`X-Shopify-Topic` if only body-derived topics are checked).
3. `Webhooks::Request.new(raw_body:, headers:)` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes the unmodified `raw_body`. [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes attacker-controlled order data as though it originated from `victim-shop`, corrupting or injecting data into the victim tenant's context.

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
