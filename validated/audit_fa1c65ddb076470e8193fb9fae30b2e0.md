Based on the investigation, I found a concrete analog to the reported bug class. Let me verify the exact webhook processing flow once more.This confirms the finding: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which only validates `request.to_signable_string` — and `Webhooks::Request#to_signable_string` returns `@raw_body` alone (`lib/shopify_api/webhooks/request.rb:36-38`). The `shop` accessor (`lib/shopify_api/webhooks/request.rb:20-23`) reads the `shopify-shop-domain` header directly, which is never included in the HMAC-signed material, yet it is forwarded unchanged into `WebhookMetadata` and handed to the app's handler as the tenant identifier (`lib/shopify_api/webhooks/registry.rb:198-199`).

### Title
Webhook shop-domain header is not bound to the HMAC-verified body, enabling cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC and then trusts the `shop-domain` header as the identity of the webhook's origin shop, even though that header is never part of the HMAC-signed content.

### Finding Description
`Registry.process` raises `Errors::InvalidWebhookError` unless `Utils::HmacValidator.validate(request)` succeeds: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` is defined to be `@raw_body` only: [3](#0-2) 

But `shop` is a separate accessor that reads the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the HMAC digest: [4](#0-3) 

After the HMAC check passes, `Registry.process` forwards this unverified `request.shop` straight into `WebhookMetadata`, which is handed to the app's registered handler as the tenant identifier for the event: [5](#0-4) 

The equality that should hold is: `shop that produced the HMAC-signed payload == shop attributed to the event by the handler`. Because the signature covers only `raw_body`, and the app's own `api_secret_key` is shared across every shop that has installed the app, any body/signature pair that Shopify legitimately generates for **one** installation (e.g., an attacker's own store) remains a valid `(raw_body, hmac)` pair regardless of which `shop-domain` header value accompanies it. An attacker who has installed the app on their own shop can capture a genuine webhook delivery for their store (valid body + valid HMAC, since Shopify signs with the app's single shared secret), then replay the exact same body and HMAC header to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Registry.process` still finds the HMAC valid (it only checks the body) and calls the handler with `shop` set to the victim's domain and `body` containing the attacker's own webhook payload.

### Impact Explanation
Any host application that follows the documented pattern of using `WebhookMetadata#shop` (or `Request#shop`) as the trusted tenant key to look up sessions, write per-merchant data, or scope side effects will process attacker-supplied webhook data under a different, victim merchant's identity. This is a cross-tenant boundary break: data or actions attributed to shop A can actually be attacker-controlled content originating from shop B's legitimate (but replayed) webhook, without needing the app's `client_secret`, an access token, or any credential belonging to the victim shop.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free/trial) installer of the target app on their own store — a normal unprivileged capability for any public or unlisted Shopify app. No secret material belonging to the app or the victim shop is needed; the attacker only needs to intercept/replay one of their own genuine webhook deliveries with a modified header, which is a standard HTTP replay a script-kiddie-level attacker can perform.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header values into the HMAC-signed material verified by `HmacValidator`, or otherwise cryptographically tie the header-derived shop to the specific delivery (e.g., cross-check against a shop-scoped webhook secret, or require the caller to supply/validate the expected shop out-of-band before trusting `request.shop`). At minimum, update `Webhooks::Request#to_signable_string` so verification covers the full set of security-relevant headers, not just the raw body, and document clearly that `Request#shop` is unauthenticated if this cannot be changed for backward-compatibility reasons.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real event (e.g. creates an order), causing Shopify to POST a webhook to the app's endpoint with a genuine `x-shopify-hmac-sha256` computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures this request: `raw_body = B`, `hmac header = H` (valid for `B` under the shared secret).
3. Attacker resends the request to the same endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and matches `H`, so validation succeeds.
5. The registered handler is invoked with `WebhookMetadata.topic`, `.body` from the attacker's own event, but `.shop == "victim-shop.myshopify.com"`, causing the host application to process attacker-controlled data as if it originated from the victim shop.

### Citations

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
