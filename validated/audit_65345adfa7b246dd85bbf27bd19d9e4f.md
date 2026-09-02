This confirms the finding: the gem's documented API (`docs/usage/webhooks.md#Process a Webhook`) explicitly tells app developers to trust `data.shop` from `WebhookMetadata`, and `ShopifyAPI::Webhooks::Registry.process` treats a valid HMAC as sufficient authentication for the whole `WebhookMetadata` object, including `shop`, `topic`, and `webhook_id` — none of which are covered by the HMAC.

### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that the HMAC matches the body, then builds `WebhookMetadata` from these unauthenticated header values and hands it to the app's handler as trusted data [3](#0-2) .

### Finding Description
The identity binding that should hold is: `HMAC(raw_body, api_secret_key) == received_hmac` **should imply** `(shop, topic, webhook_id, body)` as a whole tuple is authentic. Instead, only `body` is bound to the HMAC via `to_signable_string` [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors read straight from headers with no cryptographic tie to the signature [2](#0-1) .

`HmacValidator.validate` only recomputes and compares the signature over `to_signable_string` [4](#0-3) , so it never checks that the `shop-domain`, `topic`, or `webhook-id` headers match what Shopify actually signed for that specific webhook delivery. `Registry.process` then trusts `request.shop` as-is when constructing `WebhookMetadata`, which is documented as the authoritative tenant identifier that host apps should key their tenant-scoped logic off of [5](#0-4) .

This means any legitimate webhook body+HMAC pair a merchant possesses (e.g. one generated for their own shop and delivered to their own webhook endpoint) remains a valid `(body, hmac)` pair regardless of which `shop-domain`/`topic`/`webhook-id` header value accompanies it, because those fields are never part of the signed content.

### Impact Explanation
An attacker who operates their own Shopify store (an unprivileged app user relative to other tenants of the same app) receives genuine webhook deliveries containing a body and a valid HMAC computed with the app's `api_secret_key` over that body. Nothing in this gem prevents that attacker from replaying the identical `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` header (and/or `topic`/`webhook-id` headers) with a different, victim shop's identity. `HmacValidator.validate` still succeeds because it only checks the body against the signature [6](#0-5) , and `Registry.process` forwards the attacker-chosen `shop` value to the handler as authenticated data [7](#0-6) . Any host application that follows the gem's documented pattern of trusting `data.shop` to scope database writes, tenant lookups, or business logic (as shown in the gem's own docs) will process the attacker's data under another shop's identity — a cross-tenant access/data-poisoning scenario.

### Likelihood Explanation
Requires only that the attacker controls one legitimate shop that installs the target app and has visibility into that shop's own outbound webhook deliveries (body + HMAC), which is straightforward for any merchant. No access to `api_secret_key`, TLS interception, or privileged accounts is needed — only observation of one's own webhook traffic and the ability to POST an HTTP request with modified headers to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content that `HmacValidator` verifies (or otherwise cryptographically bind them to the request, e.g. by validating them against Shopify's registered subscription for that shop before dispatch), so that the accepted HMAC certifies the entire `WebhookMetadata` tuple, not just the raw body.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` with the app installed and subscribes to `orders/create`.
2. Shopify delivers a webhook to the attacker's shop with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` from their own delivery (trivial, since it's addressed to them).
4. Attacker sends a forged POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` and any `x-shopify-topic`/`x-shopify-webhook-id` of choice.
5. `ShopifyAPI::Webhooks::Request.new` accepts the headers [8](#0-7) ; `Utils::HmacValidator.validate` recomputes HMAC over body `B` only and it matches `H`, so validation passes [4](#0-3) .
6. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: B, ...)` and invokes the app's handler as if this were an authentic webhook for the victim shop [9](#0-8) .

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
