Confirmed: `WebhookMetadata` is constructed directly from unauthenticated headers, with `shop`, `topic`, `webhook_id`, and `api_version` all sourced from `request.shop`/`request.topic`/etc. (raw headers), while the HMAC only covers the raw JSON body.I now have sufficient evidence to confirm the root cause: `Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC (verified in `HmacValidator.validate_signature`) covers nothing but the JSON body bytes, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from attacker-visible/replayable HTTP headers and passed unauthenticated into `WebhookMetadata`, which apps use as the tenant identity for the webhook.

### Title
Webhook shop/topic/id identity fields are not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`), but the webhook HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the identity binding: `hmac-verified-bytes == raw_body ≠ shop/topic/webhook_id used to attribute the event to a tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`HmacValidator.validate_signature` computes and compares the HMAC only over that signable string: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled from the (unauthenticated) headers, not from any signed field: [3](#0-2) 

`Registry.process` validates only the HMAC and then constructs `WebhookMetadata` — the object apps use to attribute the event to a shop — directly from those unauthenticated header values: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no cryptographic binding to the HMAC-covered body: [5](#0-4) 

Because Shopify signs webhooks for all shops installed on an app using the same shared `api_secret_key` (the app's `client_secret`), any `(raw_body, hmac)` pair that is valid for one shop's webhook is also a valid `(raw_body, hmac)` pair when replayed with a different `shopify-shop-domain` (or `shopify-topic`/`shopify-webhook-id`) header value — the signature check in `HmacValidator.validate` cannot detect the substitution because it never inspects those headers. An unprivileged user who operates their own shop with the vulnerable app installed receives genuine, validly-signed webhook deliveries; they can capture one and resend it directly to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop, and the same body/hmac will still pass validation, causing the host app to process the event as if it originated from the victim tenant.

### Impact Explanation
This is a cross-tenant identity-binding failure: the app-level authorization decision ("which shop does this event belong to") is made from data the HMAC does not protect. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up a session/tenant and perform writes, deletions, or `app/uninstalled`, `customers/redact` handling), this can lead to cross-tenant data corruption or unauthorized actions attributed to another merchant's store — a Critical-class cross-tenant access issue per the impact criteria.

### Likelihood Explanation
Exploitation requires only capturing one legitimate webhook delivery from the attacker's own shop installation (trivial, since they control that shop and its outbound webhook payloads/logs) and replaying it to the app's public webhook endpoint with a modified `shop-domain` header — no access to `api_secret_key`, access tokens, or TLS interception is needed, and no host-application misuse of documented APIs is required; the gem's own `Registry.process`/`HmacValidator.validate` accepts the tampered request as-is.

### Recommendation
Include the identity-binding headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification (or otherwise cryptographically bind them to the signed payload), so that `to_signable_string` cannot be satisfied by a valid signature computed over the body alone while the shop/topic/id are swapped.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop `attacker.myshopify.com` and receives a real, Shopify-signed webhook: `raw_body = '{"id":123,...}'`, `x-shopify-hmac-sha256 = HMAC(api_secret_key, raw_body)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only [2](#0-1)  — it matches, since the body/hmac pair is untouched.
4. `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` taken straight from the header [6](#0-5)  and invokes the app's handler, which now processes attacker-controlled event data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
