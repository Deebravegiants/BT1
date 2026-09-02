### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC exclusively against that body. The `shop`, `topic`, and `webhook_id` values that `Registry.process` uses to authorize and dispatch the webhook to a handler are read straight from HTTP headers that are never part of the signed material. This is the same bug class as the reported issue: a field that drives critical control flow (`isEnabled` there, `shop`/`topic` here) is acted upon without being covered by the check that is supposed to bind it to the verified data.

### Finding Description
The HMAC binding equality that should hold is:
`shop used to dispatch webhook handler == shop cryptographically bound by the HMAC signature`

In `lib/shopify_api/webhooks/request.rb:11-38`, `hmac` is read from the `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop`, `topic`, and `webhook_id` are all read directly from unauthenticated headers with no cross-check against the signed body: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`, i.e. the raw body: [4](#0-3) 

`Webhooks::Registry.process` accepts the request once the body-only HMAC passes, then dispatches using the unauthenticated `request.topic` and `request.shop` fields: [5](#0-4) 

Because the `shop-domain` and `topic` headers are never bound to the signature, a party that has legitimately received one valid webhook delivery (body + HMAC pair) for their own shop can resend that exact body/HMAC pair to the app's webhook endpoint while substituting arbitrary `x-shopify-shop-domain` and `x-shopify-topic` header values. `HmacValidator.validate` still succeeds (it only checks the body against the secret), and `Registry.process` will invoke the registered handler believing the event originated from the spoofed shop and topic, since `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built purely from the attacker-controlled headers.

### Impact Explanation
This breaks the shop-identity binding that host applications rely on to route webhook data to per-tenant storage (a merchant's order/product/customer data keyed by `shop`). An attacker who is a legitimate but unprivileged app user (i.e., has installed the app on their own shop and thus receives real signed webhook payloads) can cause the library to hand a webhook payload to the handler tagged with a victim shop's domain, without possessing that victim's credentials, the app's `client_secret`, or any access token. Depending on how the host app's handler uses `data.shop` (typically to select the tenant record to update), this can lead to cross-tenant data corruption or disclosure — satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Likely to be exploitable in most integrations built on this gem's documented `Webhooks::Registry.process` API, because the vulnerability lives entirely in this gem's verification code, not in host-app misuse: any handler that trusts `WebhookMetadata#shop`/`#topic` as authenticated is affected once an attacker can replay a captured body+HMAC pair with different headers to the app's public webhook endpoint (which is by design internet-reachable).

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api-version`) in the signed/verifiable material, or otherwise independently cross-validate them (e.g., against Shopify's webhook subscription registry, an allow-list of installed shops, or a per-shop secret) before dispatching to the handler. At minimum, document clearly that `shop`/`topic` from `Webhooks::Request` are unauthenticated and must be independently verified by host applications before being trusted as tenant identifiers.

### Proof of Concept
1. App merchant `A` installs the app; Shopify delivers a legitimate webhook to the app's endpoint with body `B`, `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker (merchant `A`) intercepts/logs this request from their own delivery (webhooks are often replayed/logged by the app or visible via their own infra).
3. Attacker resends the identical body `B` and HMAC `H` to the app's webhook endpoint, but changes headers to `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic`.
4. `ShopifyAPI::Webhooks::Request.new` parses these headers unmodified; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`.
5. `ShopifyAPI::Webhooks::Registry.process` looks up the handler for the (attacker-chosen) topic and invokes it with `shop: "victim-shop.myshopify.com"`, causing the host application's per-tenant logic to operate on the wrong tenant using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
