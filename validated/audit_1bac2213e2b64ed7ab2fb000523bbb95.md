This confirms the vulnerability path. The gem's documentation explicitly states `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and instructs app developers to trust `data.shop` as "the shop domain of the webhook" [2](#0-1)  — yet the HMAC only signs the raw body, never the shop-domain header.

### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers and passed straight through to the app's handler after HMAC validation succeeds.

### Finding Description
`HmacValidator.validate` verifies the request by computing an HMAC over `verifiable_query.to_signable_string` and comparing it to the `hmac` field [3](#0-2) . For webhooks, `to_signable_string` is defined as `@raw_body` only [4](#0-3) , while `shop`, `topic`, `api_version`, and `webhook_id` are pulled from HTTP headers that are never included in the signable string [5](#0-4) .

`Registry.process` checks the HMAC and then immediately forwards `request.shop` (and the other header-derived fields) to the app's handler as trusted identity data, with no additional binding check: [6](#0-5) 

The identity binding that should hold is:
`shop_authenticated_by_hmac == shop_delivered_to_handler`

In reality the gem only proves `hmac_valid(raw_body) == true`; it never proves that the `shop-domain` header used to populate `WebhookMetadata#shop` is the same tenant whose body was signed. Because Shopify signs webhooks with the app's single `api_secret_key`/`old_api_secret_key` — a value shared across every shop that has installed the app, not a per-shop secret — a valid `(raw_body, hmac)` pair captured from a genuine webhook delivered for one installed shop remains cryptographically valid when replayed with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header swapped to name a different shop that also has the app installed. `HmacValidator.validate` will still return `true` since it only inspects the body, and `Registry.process` will hand the attacker-chosen `shop` string straight to the handler as `WebhookMetadata#shop` [7](#0-6) .

The documentation explicitly tells app authors that `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and that `data.shop` is simply "The shop domain of the webhook" [2](#0-1) , with no caveat that this field is unauthenticated — encouraging exactly the trust relationship this gap breaks.

### Impact Explanation
An attacker who legitimately installs the target app on a shop they control can capture a real, validly-HMAC'd webhook delivery for their own shop, then replay that same body/HMAC pair against the app's public webhook endpoint with the `shop-domain` header changed to a victim merchant's shop that also has the app installed. Because `Registry.process` treats the header-derived `shop` as authoritative once the body HMAC passes, the app's handler will process attacker-controlled event data under the victim's tenant identity — enabling cross-tenant data confusion/injection (e.g., a forged `orders/create` or `app/uninstalled` event attributed to the victim shop), which falls under the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires the attacker to have their own valid installation of the same third-party app (a normal unprivileged action, no special credentials), and requires the victim shop to also have the app installed — a realistic condition for any multi-tenant Shopify app. No access token, `client_secret`, or session compromise is needed; only observation of one's own webhook traffic and the ability to POST to the app's public webhook callback URL.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signable string, or otherwise cryptographically/contextually verify that the `shop-domain` header matches a shop for which the delivered `webhook_id`/body was actually generated (e.g., by cross-checking against Shopify's webhook metadata or requiring the host app to validate `shop` against its own installed-shop registry before trusting it). At minimum, update `docs/usage/webhooks.md` and `WebhookMetadata` to explicitly document that `shop`/`topic`/`webhook_id`/`api_version` are unauthenticated header values that must be independently validated by the host application against its known tenant list before being used for authorization decisions.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and triggers a webhook (e.g., updates an order), causing Shopify to POST a body `B` with header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's shared `api_secret_key`) to the app's webhook endpoint.
2. Attacker captures `(B, H)` from their own traffic (e.g., via a proxy they control, since it is delivered to their own server-side handler).
3. Attacker replays `POST /webhook_endpoint` with the exact same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (a shop that also has the app installed).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only presence, not correctness, is checked) [8](#0-7) .
5. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and finds it matches `H`, returning `true` [3](#0-2) .
6. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, and the app's handler acts on the forged shop identity as if it were a genuine event for the victim tenant [6](#0-5) .

### Citations

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
