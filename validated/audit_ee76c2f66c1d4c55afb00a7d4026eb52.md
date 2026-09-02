### Title
Webhook `shop` field is trusted by handlers despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively by checking the HMAC over the raw request body, then forwards `request.shop` — read from an unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header — into `WebhookMetadata` as if it were verified data. The equality the gem implicitly claims is: `hmac_valid(body) == shop_is_authentic`. That equality is false, because the HMAC signable string never includes the shop domain.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor, by contrast, is pulled straight from an HTTP header supplied by the caller, with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, immediately trusts `request.shop` to build `WebhookMetadata` that is handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) and the app's `api_secret_key`: [4](#0-3) 

Because `api_secret_key` is the app's single client secret shared across every shop that installs the app, any merchant who installs the app (an unprivileged internet action requiring no special privilege) legitimately receives webhooks with a valid HMAC over a given body. That merchant can capture a `(raw_body, hmac)` pair from their own shop's webhook delivery and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` passes the attacker-chosen `shop` value straight to the app's handler as verified data.

The gem's own documentation reinforces the false assumption that the whole request, including shop identity, is authenticated: "This will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md` line 125), and it explicitly instructs app developers to key off `data.shop` (`docs/usage/webhooks.md` lines 12-14, 25-26) without any warning that this field is unauthenticated.

### Impact Explanation
This breaks the tenant-identity binding for the only signal (`shop`) that Shopify apps use to route/act on webhook data per-tenant. An attacker who merely installs the app on their own store can forge webhook deliveries that are processed by the host app as if they originated from an arbitrary victim shop domain, since the HMAC only proves "signed by this app's secret over this body," not "this body belongs to this shop." Depending on how the host app consumes `data.shop` (e.g., looking up the shop's stored access token/session, updating tenant-scoped records, dispatching jobs keyed by shop), this enables cross-tenant confusion/access using attacker-controlled webhook bodies attributed to a victim shop.

### Likelihood Explanation
Any user can freely install a public Shopify app to become a legitimate webhook source and observe valid `(body, hmac)` pairs for topics they can trigger on their own shop (e.g., `orders/create`). Replaying that pair with a modified `shop` header requires no additional secrets, tokens, or privileged access — only knowledge of the app's public webhook endpoint, which is by design reachable from the internet.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC signable string, or otherwise cryptographically bind them to the verified payload, so `HmacValidator.validate` fails if any of these identity fields are altered post-signing. At minimum, update `ShopifyAPI::Webhooks::Request#to_signable_string` to incorporate `shop`, and document clearly that `data.shop` in `WebhookMetadata` should not be treated as authenticated unless this binding is added.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers `orders/create`, capturing the request body `B` and header `x-shopify-hmac-sha256: H` (valid because HMAC = HMAC-SHA256(api_secret_key, B)).
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `handler.handle` receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's B>, ...)`, and the host app processes attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
