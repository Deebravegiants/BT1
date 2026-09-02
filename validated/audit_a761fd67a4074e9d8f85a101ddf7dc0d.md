### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` attribute that is read directly from the unauthenticated `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `HmacValidator` only covers the raw request body. This breaks the identity binding `verified_bytes == acted_on_bytes`: the bytes that are HMAC-verified (the JSON body) are not the same bytes that `Registry.process` uses to identify which shop/tenant the webhook belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from a separate, unsigned header: [2](#0-1) 

`HmacValidator.validate` computes/compares the HMAC solely against `verifiable_query.to_signable_string`, i.e. only the body: [3](#0-2) 

`Registry.process` accepts any request whose body HMAC is valid, then forwards `request.shop` (the unauthenticated header value) straight to the app's handler as trusted tenant identity: [4](#0-3) 

Because the HMAC secret (`api_secret_key`) is a single per-app secret shared across every shop that installs the app (not per-shop), any actor who can install the app on a shop they control can obtain a genuinely-signed `(body, hmac)` pair. Since `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are never part of the signed material, that same valid `(body, hmac)` pair can be replayed to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to any other shop using the same app. The signature will still validate because it never covered the shop header in the first place.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem, following its documented API (`Registry.process`), will hand off attacker-controlled tenant identity (`shop`) as if it were verified, alongside a genuinely HMAC-validated body. Any host application logic keyed off `WebhookMetadata#shop` (e.g., updating billing state, redacting data, toggling app settings, writing to per-shop storage) can be triggered against a victim shop using a signature that was never actually issued for that shop. This is a cross-tenant access primitive, meeting the Critical bar defined for this scan.

### Likelihood Explanation
The attacker only needs to be a legitimate (even free/trial) merchant who installs the target app once to receive one authentic webhook — a routine, unprivileged action — then can replay that same authentic `(body, hmac)` against the app's public webhook URL with a forged `shop-domain` header. No access token, `client_secret`, or leaked credential is required; only the gem's documented `Registry.process` verification path is exercised.

### Recommendation
Bind the tenant/topic identity into the verified material instead of trusting separate headers: include `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) in the string that is HMAC-verified, or otherwise cryptographically bind them (e.g., derive an expected HMAC per (shop, body) tuple), so that changing the shop header without the correct corresponding signature is rejected. At minimum, document and warn integrators that `request.shop` is not authenticated by the HMAC check and must not be trusted as tenant identity without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged action), triggering Shopify to send a real webhook to the app's endpoint.
2. Attacker captures the exact `raw_body` and its accompanying `x-shopify-hmac-sha256` header from that legitimate webhook delivery.
3. Attacker sends a new POST request to the same app webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks the body against the shared `api_secret_key`: [5](#0-4) 
5. `Registry.process` invokes the handler with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, causing the host application to act on the wrong tenant using a payload/signature never issued for that shop.

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
