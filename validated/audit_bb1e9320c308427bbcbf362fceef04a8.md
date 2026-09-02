## Analog Identified: Webhook `shop` Identity Not Bound to HMAC Signature

### Title
Webhook Shop-Domain Spoofing via HMAC Scope Gap — Cross-Tenant Webhook Impersonation - ([File: `lib/shopify_api/webhooks/request.rb`])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then forwards the `shop` field taken from an **unsigned header** to the application's webhook handler as if it were an authenticated tenant identifier. This breaks the identity binding: `HMAC(raw_body) == valid` is treated as equivalent to `shop_header == authentic_tenant`, but the `shop` value is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are not covered by the signature at all: [2](#0-1) 

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` to build the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` in turn only ever checks `verifiable_query.to_signable_string` (the body) against the secret: [4](#0-3) 

The equality that should hold is:
`shop_used_by_handler == shop_that_actually_produced_this_HMAC-signed_body`

What the code actually guarantees is only:
`HMAC(raw_body, secret) == received_hmac`

Since `shop` is excluded from the signed payload, any party capable of obtaining one valid `(raw_body, hmac)` pair — for example a merchant who has the app installed on their own store and simply captures a webhook Shopify sends them — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a different shop's domain. `Registry.process` will accept it as valid and hand the forged `shop` straight to the application handler, which typically uses it to look up per-tenant records/sessions.

### Impact Explanation
This is a cross-tenant identity spoofing primitive delivered entirely by this gem's own webhook verification path: an unprivileged internet user who merely has (or captures) one legitimately signed webhook body can impersonate any other shop's webhook traffic to the app. Depending on how the host app models `shop` from `WebhookMetadata`, this can lead to cross-tenant data writes/reads keyed off the spoofed shop domain — matching the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Requires no access token, `api_secret_key`, or privileged account — only a single genuine webhook (obtainable by any merchant who installs the app, or by intercepting one delivery) and the ability to send an HTTP request with modified headers. No cryptographic secret needs to be known or broken.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material verified by `HmacValidator`, or explicitly require callers of `Registry.process` to cross-check `request.shop` against the shop associated with the destination endpoint/session before trusting it in `WebhookMetadata`. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should not allow the `shop` field to be treated as authenticated when it is excluded from `HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` (a normal, unprivileged action) and receives a legitimate webhook, e.g. body `{"id":1}` with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers without validating `shop` against anything.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body HMAC — see `lib/shopify_api/webhooks/registry.rb:190` and `lib/shopify_api/utils/hmac_validator.rb:13-22`.
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, despite the payload never having been authenticated for that shop — see `lib/shopify_api/webhooks/registry.rb:198-199`.

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
