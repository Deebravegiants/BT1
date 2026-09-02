Based on my investigation, I found a concrete instance of the exact bug class flagged in the rules: **a field acted on but not covered by the HMAC**.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` field from the unauthenticated `x-shopify-shop-domain` HTTP header, while `#to_signable_string` used by `HmacValidator` only covers the raw request body. The identity field the host application acts on (`shop`) is never bound into the value that the HMAC actually authenticates.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string` [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body`, excluding all headers [2](#0-1) . However, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed bytes [3](#0-2) . `Registry.process` validates only the HMAC of the body and then forwards `request.shop` straight to the handler as the trusted tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) .

The equality the gem should enforce is: `shop-that-signed-this-payload == shop-the-handler-is-told-it-is-for`. Because the HMAC only binds `raw_body` and not `shop`, this equality is never checked — any value of `shop-domain` header passes as long as the body+HMAC pair is valid for *some* shop.

### Impact Explanation
An unprivileged internet user who legitimately installs the app on their own store receives genuinely HMAC-signed webhook deliveries for that store (e.g. `app/uninstalled`, `shop/update`). Nothing prevents them from capturing the `raw_body` + `x-shopify-hmac-sha256` pair from that delivery and replaying it against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` (the body bytes and signature are unchanged and valid), and `Registry.process` dispatches the handler with `shop` set to the attacker-chosen victim domain. If the host app's handler trusts `data.shop` (as the library's own docs and generated `WebhookMetadata` encourage) to look up/mutate per-tenant state — most critically the `app/uninstalled` topic, which apps typically use to delete stored access tokens/sessions — this becomes a cross-tenant credential/state manipulation: an attacker can force deletion or mutation of another merchant's stored session data by relabeling their own legitimately-signed webhook as belonging to that merchant.

### Likelihood Explanation
High: no privileged access, secrets, or social engineering are required — only that the attacker install the app once on a shop they control (which any Shopify merchant/developer can do) and be able to send an HTTP request to the app's public webhook endpoint with attacker-controlled headers, both of which are normal, expected capabilities of an "unprivileged internet user" interacting with a Shopify app.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed material verified by `HmacValidator`, or otherwise cryptographically bind the shop domain to the payload, rather than trusting the unauthenticated header value passed to `WebhookMetadata`. At minimum, document and/or enforce that host applications cross-check `request.shop` against a shop they expect for that specific webhook subscription (e.g., a registered callback per-shop) rather than treating the header as trusted input.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, then triggers `app/uninstalled` (by uninstalling), receiving a genuine POST with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and some `raw_body`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` builds the request from these headers; `Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only and it matches, so validation succeeds [5](#0-4) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)`, causing the host app to process an uninstall/session-deletion event for a shop the attacker never controlled.

### Citations

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
