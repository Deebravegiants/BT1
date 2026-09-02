This confirms the finding: the gem's documentation explicitly tells app developers that "this will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`) and that `data.shop` is "The shop domain of the webhook" [1](#0-0)  which host apps are expected to use directly for shop-scoped routing (as shown in the example calling `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [2](#0-1) . This is a documented, intended API contract of the gem itself (not something the host app is misusing against undocumented behavior), so it is in scope.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [3](#0-2) , while `request.shop` is read from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header [4](#0-3) . `Utils::HmacValidator.validate` verifies the HMAC exclusively over `to_signable_string` (the raw body) [5](#0-4) , and `Registry.process` uses that same unauthenticated `request.shop` value to build the `WebhookMetadata` handed to the app's handler [6](#0-5) .

### Finding Description
The identity binding that should hold is:
`shop-domain-used-by-handler == shop-domain-cryptographically-bound-by-HMAC`

In this gem, that equality does not hold. The HMAC is computed as `HMAC-SHA256(api_secret_key, raw_body)` — a function only of the body bytes [3](#0-2) [7](#0-6) . The `shop` (and `topic`, `webhook_id`, `api_version`) values are taken straight from HTTP headers that are never included in the signed material [8](#0-7) .

Because the merchant identity is not part of the signed payload, any request whose body+HMAC pair is valid for *some* shop (e.g., the attacker's own shop, since anyone can install a public app on their own store and legitimately receive real, correctly-signed webhooks for it) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to a victim shop that also has the app installed. The HMAC check in `Registry.process` still passes because it only re-derives the signature from the untouched body [9](#0-8) , and `WebhookMetadata` is constructed with `shop: request.shop` taken from the attacker-controlled header [10](#0-9) .

The gem's own documentation instructs host apps to trust `data.shop` as "the shop domain of the webhook" after `Registry.process` returns without error [1](#0-0) [2](#0-1) , and states that `process` "will verify the request did indeed come from Shopify" [11](#0-10) . This is a stronger guarantee than the code actually provides: it verifies only that the *body* came from Shopify for *some* shop, not that the *shop* header is authentic.

### Impact Explanation
This is directly analogous to the referenced report's root cause pattern: a value that is acted upon by the application (the change-recipient/shop identity) is not fully covered by the cryptographic check that is supposed to bind it. Here, an unprivileged internet user who can install the target app on their own Shopify store (a normal, unprivileged action) can harvest genuinely-signed webhook bodies and then forge the tenant/shop association for any other installed shop, causing the host application to attribute attacker-supplied data/events to a victim tenant. Depending on how the host app uses `data.shop` (e.g., to look up the victim's session/access token, update per-shop records, or trigger shop-scoped side effects), this can result in cross-tenant data corruption or cross-tenant action execution — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitability requires only: (1) the ability to install the app on an attacker-controlled shop (unprivileged, no special access needed), (2) capturing one legitimate webhook body+HMAC pair from that shop, and (3) POSTing it to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or the victim shop is required. Likelihood is moderate-to-high wherever a host app actually uses `data.shop` for tenant-sensitive logic, which the gem's own documented usage pattern encourages.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the material that is authenticated, or at minimum cross-check the header-derived `shop` against data embedded in the verified body/session store before trusting it for tenant routing. Concretely: include the `shop-domain` header value in `to_signable_string`, or require host apps to independently confirm that `request.shop` corresponds to a shop with an active app installation/session before acting on the webhook.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) legitimately, capturing the raw body `B` and the resulting `X-Shopify-Hmac-SHA256` header value `H` (correctly computed as `HMAC-SHA256(api_secret_key, B)`).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, headers `X-Shopify-Hmac-SHA256: H`, `X-Shopify-Topic: orders/create`, and `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers without validating any relationship between `shop` and `hmac` [12](#0-11) .
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only, which matches `H`, so validation succeeds [13](#0-12) .
5. `Registry.process` invokes the host app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)` [10](#0-9) , causing the host app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
