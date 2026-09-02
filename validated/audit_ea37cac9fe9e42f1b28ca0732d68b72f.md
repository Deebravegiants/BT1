I have enough evidence to construct the analog finding.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`, `webhook_id`, `api_version`) values from HTTP headers, while `Utils::HmacValidator` only authenticates the raw request body. This breaks the identity binding: `shop_authenticated == shop_used_for_tenant_attribution` does not hold, because the HMAC signature is computed and verified purely over `@raw_body`, never over the `shop` header.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate`/`validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` field: [2](#0-1) 

Yet `Registry.process` uses `request.shop` (parsed straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, with no cryptographic binding) to build the `WebhookMetadata` that is handed to the app's webhook handler: [3](#0-2) [4](#0-3) 

Because a single `api_secret_key` is shared by an app across *all* installed shops (multi-tenant SaaS model), any unprivileged internet user who installs the app on their **own** free/dev store legitimately receives real webhooks whose bodies are genuinely HMAC-signed by Shopify with that shared secret. The attacker fully controls the HTTP request that eventually reaches the app's webhook endpoint (it's just an HTTP POST to a public URL), so they can take a real, validly-signed `(body, hmac)` pair from their own store's webhook and resubmit it with the `X-Shopify-Shop-Domain` header swapped to a victim shop's domain. `HmacValidator.validate` will still pass — it only checks the body/hmac pair, which is unchanged and genuinely valid — but `Registry.process` will attribute the (attacker-controlled) body content to the victim shop when invoking the handler: [5](#0-4) 

This is the same bug class as the report's "input/identity validation" theme, generalized to an equality that is never checked: `hmac_verified_bytes == raw_body` but `tenant_identity_used_by_handler == shop_header`, and these two are never cryptographically tied together.

### Impact Explanation
This is a cross-tenant vulnerability (Critical per the given impact categories): a merchant using the same app (or anyone able to freely create a Shopify dev/trial store to install the app) can forge webhook deliveries that the host application will attribute to a different, arbitrary shop domain, while carrying an HMAC that legitimately validates. If the host application uses `WebhookMetadata#shop` for anything security-relevant (e.g., looking up/mutating that shop's stored data, triggering redaction/GDPR flows, updating billing/plan state, or feeding data into per-shop records) — which is exactly what the field exists for — the attacker can inject or corrupt data across tenant boundaries without ever needing the app's `api_secret_key`, an access token, or any privileged credential.

### Likelihood Explanation
The prerequisite is only that the attacker can install the target app on any shop they control (a standard, unprivileged action available to the public for most apps in the Shopify App Store, or via a free development store) and can send arbitrary HTTP requests to the app's public webhook endpoint (which by design must be internet-reachable). No secrets, tokens, or elevated access are required — only reuse of a header value that is neither signed nor bound to the payload.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the HMAC-verified signable string, or otherwise cryptographically tie the header claims to the payload before trusting them for tenant attribution — e.g., have `Request#to_signable_string` incorporate the normalized headers alongside the raw body, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signed parameter set: [6](#0-5) 

### Proof of Concept
1. Attacker signs up for a free/dev Shopify store and installs the target app, becoming a legitimate merchant of that app (shares the same `api_secret_key` as every other installation).
2. Shopify sends the attacker's store a genuine webhook, e.g. `orders/create`, with body `B` and a correctly computed `X-Shopify-Hmac-Sha256` header `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker intercepts this legitimate delivery (e.g., via a proxy they control as the endpoint owner, or by reusing `curl` against the app's public webhook URL) and resends `POST /webhooks` with the same body `B` and same `H`, but replaces `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC-SHA256(api_secret_key, B) == H` — this still passes since `B` and `H` are untouched: [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the host app to process attacker-supplied data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
