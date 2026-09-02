## Finding

### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Webhooks::Registry.process` verifies only that HMAC against the body. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read straight from HTTP headers and passed on to the app's handler without themselves being covered by the HMAC. Anyone who possesses one valid `(raw_body, hmac)` pair signed with the app's secret (e.g. a merchant who installed the app on their own store and received a genuine webhook) can replay the same body/HMAC pair while substituting arbitrary values in the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers, and the request will still pass verification.

### Finding Description
The verification chain is: [1](#0-0) 
Only `@raw_body` is included in the signable string, and `shop`, `topic`, `webhook_id`, `api_version` are pulled directly and unauthenticated from headers: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body, then trusts `request.shop`/`request.topic`/`request.webhook_id` to build the metadata dispatched to the app's handler: [3](#0-2) 

The HMAC validator itself only ever recomputes the signature over `verifiable_query.to_signable_string`, i.e. the body, and never incorporates the headers: [4](#0-3) 

This breaks the identity binding `shop authenticated == shop the handler acts on`: the HMAC authenticates the body's integrity/origin (that it was signed by the app's `api_secret_key`), but the `shop` value that the handler uses to key its business logic (e.g. "which tenant's data to update") is taken from an unauthenticated header. A merchant who has genuinely installed the app on their own store (`shop-a.myshopify.com`) and thus legitimately receives HMAC-valid webhooks can capture one such `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with `x-shopify-shop-domain: shop-b.myshopify.com` (or any other tenant they want to target). `Utils::HmacValidator.validate` still returns `true` because it never looks at the headers, and `Registry.process` dispatches to the handler with `shop: "shop-b.myshopify.com"`.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem hands the app's webhook handler a `shop` (and `topic`/`webhook_id`) value that is not cryptographically bound to the authenticated payload. Any app whose webhook handlers use `data.shop` to select which tenant's session/record to act on (which is the documented, expected usage pattern per `docs/usage/webhooks.md`) can be tricked into performing actions or making data changes attributed to a shop the attacker doesn't own, using only a body/HMAC pair the attacker legitimately obtained for their own shop. This matches the "cross-tenant access" criterion.

### Likelihood Explanation
High. Any app developer using this gem's own documented `Registry.process` flow inherits this gap automatically — no misuse of the API is required. The only prerequisite is that the attacker has (or can obtain) one legitimate webhook body+HMAC pair for their own installed shop, which is trivial since any merchant can install the app on a shop they control and observe a genuine webhook delivery.

### Recommendation
Bind the `shop`, `topic`, `webhook_id`, and `api_version` header values into the signed payload verification — e.g., include the relevant headers in `to_signable_string`, or otherwise cryptographically bind the shop-domain to the HMAC-verified content before it's handed to the handler, rather than trusting these headers implicitly.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`. Shopify sends a real webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `api_secret_key`, plus `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture the raw body and HMAC header value.
3. Resend the same raw body and same HMAC header, but replace `x-shopify-shop-domain` with `victim.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over the raw body — it still matches, so verification passes.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process/act as if the webhook genuinely originated from `victim.myshopify.com`.

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
