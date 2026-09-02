Confirmed: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates only `Utils::HmacValidator.validate(request)`, which HMACs `request.to_signable_string` — and `Webhooks::Request#to_signable_string` returns just `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), never the `shop`, `topic`, or `webhook_id` headers. Yet the handler is invoked with `request.shop`, `request.topic`, and `request.webhook_id` taken directly from unauthenticated headers (`lib/shopify_api/webhooks/registry.rb:198-199`) and trusted as the tenant identity for the event.

### Title
Webhook shop/topic/webhook-id headers are trusted for tenant identity but excluded from the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw HTTP body, never the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers [1](#0-0)  . `Registry.process` accepts the request purely on the strength of `Utils::HmacValidator.validate(request)` and then forwards `request.shop`, `request.topic`, and `request.webhook_id` verbatim to the app's registered handler as trusted tenant metadata [2](#0-1)  .

### Finding Description
The equality the gem is implicitly asserting is: `shop_header_value == shop_the_body_belongs_to`. But the HMAC only binds `body -> signature`; it never binds `shop -> signature` or `topic -> signature`. Because a single app's `client_secret` (and therefore the HMAC key, `Context.api_secret_key`) is shared across every merchant/tenant that installs the app, any request body that was legitimately HMAC-signed by Shopify for one tenant produces a signature that is *still valid* when the same body is resubmitted with a different, attacker-chosen `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header. `HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the secret [3](#0-2)  — it has no way to detect that the tenant-identifying headers were swapped, since those headers were never part of what got signed.

### Impact Explanation
An unprivileged internet user who is a legitimate low-privilege merchant of the multi-tenant app (i.e., they have their own store installed, and Shopify genuinely sends them HMAC-signed webhooks for their own shop's events) can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to point at a different tenant of the same app. `Registry.process` will accept it as authentic (HMAC checks out) and dispatch it to the handler with `WebhookMetadata#shop` set to the spoofed victim shop [4](#0-3) . Any host application that uses `data.shop` to look up records, trigger side effects, or attribute the event (which is the documented, expected usage pattern) will process attacker-controlled data under another tenant's identity — this is a cross-tenant data/action confusion that crosses the multi-tenant boundary without requiring the app's `client_secret`, an access token, or any credential of the victim tenant.

### Likelihood Explanation
Requires only: (1) that the attacker be a real, if low-privileged, installed merchant of the same app (so they legitimately receive at least one genuine signed webhook), and (2) that they can POST to the app's public webhook endpoint with modified headers, which is standard, unauthenticated HTTP access. No secrets, tokens, or social engineering are needed — this fits squarely in the "unprivileged internet user" threat model.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the signed payload verification, or otherwise cryptographically bind them to the body before trusting them — e.g., verify that the signature was generated for this specific `(shop, body)` pair, or require host apps to independently corroborate `shop` against a value obtained through an authenticated channel (such as the session that originally registered the webhook) rather than trusting the raw header value directly.

### Proof of Concept
1. App merchant A installs the app; Shopify sends a real webhook to the endpoint: `raw_body = B`, headers include `shopify-shop-domain: A.myshopify.com`, `shopify-hmac-sha256: H` where `H = HMAC-SHA256(secret, B)`.
2. Merchant A (attacker) captures `(B, H)`.
3. Attacker crafts a new POST to the same endpoint with `raw_body = B` (unchanged) and `shopify-shop-domain: B.myshopify.com` (victim tenant), `shopify-hmac-sha256: H` (unchanged).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...spoofed shop...})` builds successfully since required headers are present.
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(secret, B)` and compares to `H` — this matches because only `B` is signed, so validation passes despite the shop header being forged.
6. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "B.myshopify.com", body: ..., ...))` is invoked, and the host app processes an event as though it genuinely originated from tenant B, when it actually contains tenant A's body content and was never signed for tenant B.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
