Confirmed: `WebhookMetadata.shop` (and `.topic`) is the exact value passed to app handlers via `WebhookHandler#handle`, sourced directly from the unauthenticated header, with no cryptographic binding to the verified body.### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`) attribute solely from HTTP headers (`x-shopify-shop-domain` / `shopify-shop-domain`), while `Utils::HmacValidator` only verifies the raw request body via `to_signable_string`. The `shop` value is never part of the signed payload, so it can be freely modified without invalidating the HMAC. `Registry.process` trusts this unauthenticated `shop` value and forwards it directly to the host application's webhook handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from caller-supplied headers, none of which are included in the signed string: [2](#0-1) 

`Registry.process` validates only the HMAC over the body/signature pair, then immediately trusts `request.topic` and `request.shop` to route and label the payload for the app's handler: [3](#0-2) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` header — again, `to_signable_string` for a webhook `Request` is just the body: [4](#0-3) 

The identity binding that should hold is: `shop attributed to webhook data == shop cryptographically bound by the signed payload`. In this gem it instead holds only: `shop attributed to webhook data == shop header value` (unauthenticated), while the HMAC binds nothing but the JSON body bytes. Because the app's `client_secret` is shared across every shop that installs the app, any merchant who installs the app can legitimately receive a validly-signed webhook for their own store, then replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The HMAC remains valid (it only signs the body), but `WebhookMetadata.shop` — the field the host app uses to decide "whose data is this" — is now attacker-controlled: [5](#0-4) 

### Impact Explanation
This breaks the tenant-identity binding this gem is supposed to enforce for webhook delivery: `handler.handle` receives `WebhookMetadata` whose `shop` is not covered by the cryptographic check performed by `Registry.process`, only the body is. Any host application that (as documented/intended) relies on `WebhookMetadata#shop` from `ShopifyAPI::Webhooks::Registry.process` to decide which merchant record to update, delete, or notify can be tricked into applying one merchant's legitimately-signed webhook payload under a different merchant's identity — a cross-tenant data-integrity/confidentiality break driven entirely by an unauthenticated header. This satisfies the "cross-tenant access" criterion for High/Critical impact since it lets one unprivileged merchant (who only needs to install the app once) cause data attributed to another tenant.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must be able to install the app on at least one shop (a normal unprivileged action for any Shopify merchant) to obtain one validly-HMAC-signed webhook body, then can reuse that valid `(body, hmac)` pair with an arbitrary `shop`-domain header value pointed at any target shop, since `Utils::HmacValidator` never checks that the shop header matches anything cryptographically. No access to `api_secret_key`, access tokens, or the target's credentials is required — only a replayed/edited HTTP request to the app's own webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`) into the HMAC-verified signable string, e.g. include the relevant Shopify headers in `to_signable_string` for `Webhooks::Request`, or otherwise cryptographically bind the shop domain to the payload before it's handed to `WebhookMetadata`/`WebhookHandler#handle`. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against a known-installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker.myshopify.com`) and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body B>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: B
   ```
2. Attacker resends the same request to the app's webhook endpoint, only changing the shop header:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim.myshopify.com
   Body: B
   ```
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only (`request.rb:35-38`, `hmac_validator.rb:26-31`) — validation succeeds because the body `B` is unchanged.
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "victim.myshopify.com"` (`registry.rb:198-199`), even though this webhook was never actually sent by Shopify for `victim.myshopify.com`.
5. Any host application logic that trusts `WebhookMetadata#shop` to select which tenant's data to mutate now processes attacker-controlled data under the victim's identity.

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
