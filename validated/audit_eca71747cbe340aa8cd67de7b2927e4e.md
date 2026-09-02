Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC of the body and then trusts `request.shop` from the header to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook `shop` (and topic/version/id) identity fields are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the HMAC over the raw request body only [4](#0-3) [1](#0-0) , but the `shop`, `topic`, `api_version`, and `webhook_id` fields that the app relies on to attribute the event to a tenant are read straight from HTTP headers with no cryptographic binding to the signed payload [2](#0-1) . `Registry.process` accepts the request once `Utils::HmacValidator.validate(request)` passes and then forwards `request.shop` (from the header) into the merchant-facing handler untouched [3](#0-2) .

### Finding Description
The binding the gem is expected to enforce is: `shop header == shop the signed body actually originated from`. Because `to_signable_string` only returns `@raw_body` [1](#0-0) , the HMAC proves only "this body byte-sequence was signed with the app's `api_secret_key`" — it says nothing about which shop the header claims it came from. All shops that install a given app share the same `api_secret_key`, so any merchant who has legitimately installed the app can obtain genuinely-HMAC-signed webhook bodies for their own store (e.g. by triggering `orders/create` on their own dev/test shop and capturing the outgoing webhook payload/HMAC sent to the app's shared endpoint). That attacker-controlled merchant can then replay the exact same raw body and HMAC value to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a victim shop. `HmacValidator.validate` will still pass because it only recomputes the HMAC over `@raw_body` [5](#0-4) , and `Registry.process` will dispatch to the handler with `shop: request.shop` pointing at the victim tenant while `body: request.parsed_body` is actually attacker-controlled content [6](#0-5) .

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an unprivileged attacker (any merchant who installed the app) can make the host application process attacker-chosen webhook data under another shop's identity, since the gem never binds `shop`/`topic`/`webhook_id` to the signed bytes. Depending on what the host app's webhook handlers do with `shop` (e.g., look up/mutate stored per-shop data, trigger side effects, or write audit logs keyed by shop), this enables cross-tenant data confusion or corruption — qualifying as cross-tenant access per the rules.

### Likelihood Explanation
Requires only that the attacker be a legitimate (unprivileged relative to other tenants) installer of the target app on their own shop — no access to `api_secret_key`, access tokens, or the victim's credentials is needed. The attacker just needs the ability to capture their own genuinely-signed webhook payload/HMAC and resend the HTTP request with a modified shop-domain header to the app's shared webhook endpoint, which is standard behavior for any multi-tenant Shopify app built on this gem.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the signed/verified material, or otherwise cryptographically bind them to the body before trusting `request.shop` — e.g., have `Registry.process` cross-check the header-provided shop against a value embedded in and covered by the signed payload, rather than trusting the header outright.

### Proof of Concept
1. App A is installed on Shop X (attacker-controlled) and Shop Y (victim), sharing one `api_secret_key`.
2. Attacker triggers `orders/create` on Shop X, capturing the raw body and the valid `X-Shopify-Hmac-Sha256` header Shopify sends to the app's shared webhook endpoint.
3. Attacker resends that exact body/HMAC to the same endpoint, but sets `X-Shopify-Shop-Domain: shop-y.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the HMAC [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "shop-y.myshopify.com"` but attacker-controlled `body`, causing the host app to process attacker data as if it came from Shop Y [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
