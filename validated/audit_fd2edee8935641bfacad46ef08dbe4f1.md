This confirms the finding. The docs explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the `data.shop` field is documented as "The shop domain of the webhook" for tenant-scoped processing [2](#0-1) . This is the exact identity-binding break the analog calls for: the HMAC only covers the raw body, not the `shop` header that host apps rely on for tenant identity.

### Title
Webhook `shop` identity spoofing via HMAC that only binds the request body, not the shop header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [3](#0-2) , and `HmacValidator.validate_signature` computes/verifies the HMAC exclusively over that signable string [4](#0-3) . Meanwhile `Registry.process` passes `request.shop` — sourced straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [5](#0-4)  — into `WebhookMetadata`, which the host app's handler treats as the authenticated tenant identity [6](#0-5) .

### Finding Description
The intended identity binding is: `hmac_valid ⇒ (body, shop) both authentic from Shopify`. The actual binding enforced by the code is only: `hmac_valid ⇒ body authentic`. The `shop` field carried in `WebhookMetadata.shop` — which the docs explicitly label as the trusted "shop domain of the webhook" for the handler to key its tenant-specific processing on [7](#0-6)  — is never included in the HMAC computation, so it is not cryptographically bound to the signature at all. `HmacValidator.validate` is keyed only by the app's own single `Context.api_secret_key`/`old_api_secret_key` [8](#0-7)  — the same secret is valid for every shop that has installed the app — so a valid `(body, hmac)` pair generated from one legitimately-installed shop (the attacker's own store, which they can freely trigger webhooks from) remains a cryptographically valid pair for that app regardless of which `shop` header value accompanies it.

### Impact Explanation
An attacker who has installed the target app on their own Shopify store can capture any real webhook delivered to their endpoint (a legitimate `(body, hmac)` pair, generated using the app's `api_secret_key`, which they never need to know). They can then replay that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (it only checks the body) [9](#0-8) , and `Registry.process` dispatches to the handler with `shop: request.shop` set to the victim's domain, and body content controlled by the attacker [10](#0-9) . Any host application that uses `data.shop` to look up the tenant's session/store record and applies `data.body` to that tenant's data (the exact documented pattern) will process attacker-controlled data under the victim shop's identity — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Exploitation requires only an ordinary, unprivileged Shopify Partner account to install the target app on a store the attacker controls and observe one webhook delivery — no access to `api_secret_key`, access tokens, or any privileged credential is needed. This satisfies the "unprivileged internet user" and "no privileged credential" scope constraints.

### Recommendation
Include the shop domain (and other identity-relevant headers such as `webhook_id`/topic/api_version, or minimally the shop domain) in the signable string that is HMAC-verified, or otherwise cryptographically bind the `shop` header to the signed payload before trusting it in `WebhookMetadata`. Short of a body format change (which Shopify controls), the gem should document/require that host apps additionally verify the resolved shop has an active, matching session/webhook registration before trusting `data.shop`, and note in the docs that `shop` is currently unauthenticated by the HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they legitimately control) and registers a webhook (e.g., `orders/create`) as any real merchant would.
2. Shopify delivers a webhook to the app's endpoint with headers `x-shopify-hmac-sha256: <H>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and body `B`. `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this successfully (no header/body cross-check) [11](#0-10) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and confirms it equals `H` — passing, since it never looks at the shop header [4](#0-3) .
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-chosen B>, ...)` [12](#0-11) , causing the host app to process attacker-supplied data as though it originated from the victim's store.

### Citations

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
