### Title
Webhook `shop` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop` value taken from an unsigned HTTP header to attribute the payload to a tenant. Because the header is not part of the signed material, an attacker who controls any shop that has the app installed can replay a legitimately-signed webhook body while substituting the `X-Shopify-Shop-Domain` header for a victim shop, causing the host application's handler to process attacker-supplied data as if it originated from the victim's shop.

### Finding Description
`Registry.process` validates the webhook using `Utils::HmacValidator.validate(request)` and, if valid, immediately constructs `WebhookMetadata` using `request.shop`, which is then passed to the host app's handler: [1](#0-0) 

The `Request#hmac` accessor pulls the signature straight from the `hmac-sha256` header, and the value that is actually signed (`to_signable_string`) is only the raw request body — the `shop` is read from a separate header (`shop-domain`) that plays no part in the signature computation: [2](#0-1) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac`, using only the object's `to_signable_string` (i.e. the raw body for webhooks) — it never incorporates `shop`: [3](#0-2) 

The identity binding that should hold is:
`shop_that_Shopify_actually_signed_this_body_for == request.shop_header_used_by_handler`

Because `shop-domain` is excluded from the HMAC-covered bytes, this equality is never checked. `HMAC(secret, raw_body)` is valid for *any* value of the `shop-domain` header as long as `raw_body` matches what Shopify signed for the originating shop. An attacker who owns/controls a shop that has the target app installed (an ordinary, unprivileged merchant account — no `api_secret_key`, access token, or app credential needed) receives a validly-HMAC-signed webhook from Shopify for their own shop, then replays that exact body to the app's webhook endpoint while overwriting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` hands the handler a `WebhookMetadata` whose `shop` field is the attacker-chosen victim domain, with `body` fully attacker-controlled content the attacker's own shop legitimately produced.

### Impact Explanation
This breaks the tenant-isolation boundary the gem is meant to provide to host applications: the `shop` value is the only per-tenant identity the library hands to `WebhookHandler#handle`, and host apps commonly key their data (order sync, inventory, GDPR/mandatory webhook processing, session/token bookkeeping, uninstall handling) off this `shop` value. Since one of the mandatory topics processed through this exact path is `shop/redact` / `customers/redact` / `customers/data_request` (`MANDATORY_TOPICS`), and any other registered topic goes through the identical `process` method, an attacker can trigger a handler with a forged `shop` value for arbitrary registered topics — e.g. delivering an `app/uninstalled`-style or data-mutating payload that the handler believes came from a victim shop, resulting in cross-tenant data corruption/exfiltration or unauthorized state changes for a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category: an unprivileged internet user (any merchant able to install the app on their own store) can attribute forged webhook payloads to an arbitrary victim shop domain.

### Likelihood Explanation
Likelihood is high for any host application that trusts `WebhookMetadata#shop` for authorization or record lookup (the documented and expected usage pattern, per `docs/usage/webhooks.md` and `WebhookHandler`). No secrets, tokens, or privileged access are required — only: (1) installing the target app on an attacker-controlled shop to receive one legitimately-signed webhook, and (2) replaying that HTTP request with a modified `shop-domain` header, which the gem performs no additional verification of (no comparison against a known/registered shop list, no session lookup tying the header to an actual installed shop for that specific webhook body).

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) header value in the HMAC-signed material, or otherwise cryptographically bind it to the payload before verification, so that `HmacValidator.validate` fails if the `shop-domain` header does not match the shop the body was actually signed for. At minimum, update `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` to include the shop header alongside the raw body, and update `HmacValidator`/`Registry.process` accordingly. Additionally, `Registry.process` should not release `request.shop` to handlers until the header has been shown to correspond to the currently authenticated webhook payload.

### Proof of Concept
1. App registers a webhook handler for topic `orders/create` (or any registered topic) via `ShopifyAPI::Webhooks::Registry.add_registration`.
2. Attacker installs the target app on their own store `attacker-shop.myshopify.com` (fully self-serve, unprivileged) and receives a legitimate webhook delivery from Shopify for `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of body B computed with the app's shared secret>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - body `B` (attacker fully controls the order contents on their own shop, e.g., custom line-item metadata, addresses, etc.)
3. Attacker resends the exact same HTTP request to the app's public webhook endpoint, only changing the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - Leaving `x-shopify-hmac-sha256` and body `B` unchanged.
4. Server calls `ShopifyAPI::Webhooks::Registry.process(request)`:
   - `Utils::HmacValidator.validate(request)` recomputes HMAC over `request.to_signable_string` (== `B`, the raw body) and it matches the still-present, still-valid `x-shopify-hmac-sha256`, per [4](#0-3)  and [5](#0-4) .
   - `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop = "victim-shop.myshopify.com"` (from the attacker-modified header), per [6](#0-5)  and [7](#0-6) .
   - The host app's `handler.handle(data:)` runs with attacker-controlled `body` attributed to `victim-shop.myshopify.com`.
5. Any host-app logic keyed by `data.shop` (record lookups, session correlation, deletion/redaction triggers for mandatory topics, etc.) is now executed against the victim tenant using attacker-controlled input, i.e. cross-tenant access/data injection.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
