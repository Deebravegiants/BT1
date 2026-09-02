Confirmed root cause. This is a real, gem-internal identity-binding gap: the webhook HMAC only covers the raw request body, while the `shop` (and `topic`/`webhook-id`) values that `Registry.process` hands to the app's handler are taken from unauthenticated headers.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC validated by `Utils::HmacValidator.validate` in `Registry.process` authenticates the JSON body but not the `x-shopify-shop-domain` (or `x-shopify-topic`/`x-shopify-webhook-id`) headers. `Registry.process` nonetheless takes `request.shop` straight from that unauthenticated header and hands it to the app's handler as the tenant identity for the webhook.

### Finding Description
`Registry.process` validates authenticity with: [1](#0-0) [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For webhooks, `to_signable_string` is hard-coded to the raw body only, while `shop` is read directly from an HTTP header with no cryptographic tie to the HMAC: [3](#0-2) 

The identity binding the gem should enforce is: `hmac == HMAC(secret, body || shop || topic)`. In reality the gem enforces only `hmac == HMAC(secret, body)`, leaving `shop` (the field the handler acts on to select tenant data) completely outside the authenticated envelope. An attacker who legitimately installs the app on their own store (a normal, unprivileged action) will receive real webhooks with a valid HMAC computed over a body they control the shape of (e.g. via triggering `orders/create` on their own store). Because the header carrying the victim's shop domain is never included in the signed bytes, the attacker can capture one authentic `(body, hmac)` pair from their own store and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` forwards `shop: request.shop` = the victim's domain into `WebhookMetadata`, so the host application's handler will process attacker-controlled webhook data as if it originated from the victim's store.

### Impact Explanation
This breaks the tenant-identity binding the gem is trusted to provide via `HmacValidator`: any code that relies on `WebhookMetadata#shop` (populated straight from `Registry.process`) to select which merchant's records to update, without independently re-validating the shop against its own list of installed shops, will apply attacker-supplied webhook data to another tenant's data — a cross-tenant access/data-integrity issue that Sherlock's High bar covers (scope/binding check answering permissively). It requires no access token, no leaked secret, and no privileged account — only that the attacker be an installed merchant of the same app, i.e., an unprivileged internet user relative to other tenants.

### Likelihood Explanation
Likely to be exploitable in practice: installing an app on a free/test store is trivial, webhook bodies for many topics are attacker-influenceable (e.g., `orders/create`, `products/update` on the attacker's own shop), and nothing in `Request`, `HmacValidator`, or `Registry.process` binds the `shop` header to the signed payload, so no error is raised.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header value in the string that is HMAC-verified, or otherwise cryptographically bind them to the payload before `Registry.process` forwards `request.shop` to handlers. At minimum, document that host applications must cross-check `WebhookMetadata#shop` against their own store of previously-authorized shop domains before trusting it — the gem currently gives no signal that this header is unauthenticated.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and obtains a legitimate webhook delivery: body `{"id":1}` with header `x-shopify-hmac-sha256: <valid HMAC of body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body`, `lib/shopify_api/webhooks/request.rb:36-38`, so validation passes.
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-controlled header value `"victim.myshopify.com"`, `lib/shopify_api/webhooks/registry.rb:198-199`, and the app's handler processes the forged data as belonging to the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
