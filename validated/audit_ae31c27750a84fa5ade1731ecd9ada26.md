### Title
Webhook `shop`, `topic`, `webhook-id` and `api-version` are read from unsigned HTTP headers while the HMAC only covers the raw body, allowing shop-spoofed webhook delivery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, while the shop identity (`shop-domain` header) that the host application uses to attribute the webhook to a tenant is never included in the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `topic`, `shop`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers that are not part of the signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` — which, per `HmacValidator`, recomputes the HMAC over `to_signable_string` (i.e. the body only) and compares it to the `hmac-sha256` header — and then trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop asserted in HMAC-signed bytes == shop the handler acts on`. Here, only the body bytes are authenticated; the `shop-domain` header (and `topic`/`webhook-id`/`api-version`) are unauthenticated metadata copied verbatim into `WebhookMetadata`. Any unprivileged user who has received one legitimate webhook delivery for their own shop/app installation (e.g. by installing the app on their own test store) obtains a valid `(raw_body, hmac)` pair signed with the app's real `client_secret`. Because the signature never binds to `shop-domain`, that same body+hmac pair remains valid if replayed to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim's shop domain (and/or `webhook-id`/`topic` altered, since those are also unsigned). `HmacValidator.validate` will still return `true`, and the host app's handler will process attacker-controlled or replayed body content believing it originates from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee for webhook processing: an attacker with only an unprivileged relationship to the app (their own store's genuine webhook traffic) can make the app attribute crafted/replayed events to a different merchant's shop. Since host applications typically use `WebhookMetadata#shop` to look up the corresponding session/tenant record and perform account-scoped actions (including mandatory topics like `customers/redact`, `shop/redact`, `customers/data_request`), this enables cross-tenant data confusion/injection without ever possessing the victim's credentials or access token — a cross-tenant access issue.

### Likelihood Explanation
Requires the attacker to have received at least one genuine webhook for their own store (trivial — install the app themselves) and the ability to send an HTTP request to the app's public webhook endpoint with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header while keeping the same raw body — no secret material, TLS interception, or privileged access is needed. This is a straightforward analog of the reported "identity not wiped/bound across authenticated vs. acted-upon state" bug class.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) as part of the HMAC-signed material verified against Shopify's canonical webhook signing scheme, or otherwise cryptographically bind the header-derived `shop` to the verified body before constructing `WebhookMetadata`. At minimum, document/require that `Registry.process` callers independently confirm `request.shop` corresponds to a shop for which this exact `webhook_id`/topic combination was expected, rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the resulting `shopify-hmac-sha256` header `H` (a valid HMAC-SHA256 of `B` under the app's real secret).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with the exact same body `B` and header `H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-webhook-id`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — validation succeeds: [5](#0-4) 
4. `WebhookMetadata` is built with `shop: request.shop` == `"victim-shop.myshopify.com"`, and passed to the app's handler, which processes the attacker's payload as if it came from the victim shop: [6](#0-5)

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
